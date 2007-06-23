import cStringIO
import logging, time, copy
from twisted.internet import reactor, protocol, task
from amf import amf0
import rtmputil, flv

class ProcessProtocolBufferWriter(protocol.ProcessProtocol):

    def __init__(self, buffer):
        self.buffer=buffer
        self.ended=False

    def connectionMade(self): pass

    def outReceived(self, data):
#        logging.debug("stdout: %s"%data)
        self.buffer.write(data)
#        if self.request.connectionclosed:
#            self.transport.closeStdout()
#            print "killed"
#        self.request.write(data)
        
    def errReceived(self,data):
        logging.error("stderr: %s"%data)
        
    def outConnectionLost(self): pass
    def errConnectionLost(self): pass
    def inConnectionLost(self): pass
    
    def processEnded(self, reason):
        self.ended=True
#        self.request.finish();
#        logging.info("Process ended: %s"%reason);


class RTMPProtocol(protocol.Protocol):
    HANDSHAKELENGTH=0x600
    WELCOMEBYTE= 0x03
    
    STATE_WAITINGFORHANDSHAKE = 1;
    STATE_WAITINGFORHANDSHAKE_REPLY = 2;
    STATE_EXPECTAMF = 3;
    
    HEADERSIZE=[12,8,4,1];
    
    KIND_KCHUNKSIZE=0x01
    KIND_KBYTESREADED=0x03
    KIND_KCOMMAND=0x04
    KIND_KAUDIO=0x08
    KIND_KVIDEO=0x09;
    KIND_KCALL=0x14;
    
    COMMANDKIND_CLEAR=0x00
    COMMANDKIND_PLAY=0x01
    COMMANDKIND_CLIENTBUFFER=0x03
    COMMANDKIND_RESET=0x04
    COMMANDKIND_PING=0x06

    COMMANDSIZE = {
                   COMMANDKIND_CLEAR:0,
                   COMMANDKIND_PLAY:0,
                   COMMANDKIND_CLIENTBUFFER:4,
                   COMMANDKIND_RESET:0,
                   COMMANDKIND_PING:4,
                  }

    def __init__(self):
        self.input = rtmputil.FancyReader(BufferedStringStream())
        self.output = rtmputil.FancyWriter(BufferedStringStream())
        self.sChannel = {}
        self.read_chunk_size=128
        self.write_chunk_size=128
        self.sStream={}
        self.remotecallables= {
                        "connect": self.rpcConnect,
                        "createStream": self.rpcCreateStream,
                        "play": self.rpcPlay,
                       }
        self.commands = {
                       RTMPProtocol.COMMANDKIND_CLEAR: self.cmdClear,
                       RTMPProtocol.COMMANDKIND_PLAY: self.cmdPlay,
                       RTMPProtocol.COMMANDKIND_CLIENTBUFFER: self.cmdClientBuffer,
                       RTMPProtocol.COMMANDKIND_RESET: self.cmdReset,
                       RTMPProtocol.COMMANDKIND_PING: self.cmdPing,
                       }
        
        
    def connectionMade(self):
        self.state = RTMPProtocol.STATE_WAITINGFORHANDSHAKE
        logging.info("Connected to %s." % (self.transport.getPeer( ).host));
        playflv = task.LoopingCall(self.playFLV)
        playflv.start(1)
        
    def connectionLost(self, reason):
        logging.info("Lost connection to %s." % self.transport.getPeer( ).host);
        
    def dataReceived(self, data):
        logging.debug("Received: \n%s"%getBinaryStream(data))
        self.input.write(data)
        self.checkForParsableContent()
        
    def checkForParsableContent(self):
        while True:
            if self.state == RTMPProtocol.STATE_WAITINGFORHANDSHAKE:
                self.input.transactionStart()
                try:
                    self.readWelcomeHandshake()
                except BufferedStringStreamInsufficientDataException:
                    self.input.transactionRollback()
                    return;
                self.input.transactionCommit()
                self.replyToHandshake(True)
                self.state = RTMPProtocol.STATE_WAITINGFORHANDSHAKE_REPLY
                logging.info("Handshake received");
            elif self.state == RTMPProtocol.STATE_WAITINGFORHANDSHAKE_REPLY:
                self.input.transactionStart()
                try:
                    self.readReplyHandshake()
                except BufferedStringStreamInsufficientDataException:
                    self.input.transactionRollback()
                    return;
                self.input.transactionCommit()
                self.replyToHandshake(False)
                self.handshake=None # we won't need it any longer
                self.state = RTMPProtocol.STATE_EXPECTAMF
                logging.info("Handshake Reply received");
            elif self.state == RTMPProtocol.STATE_EXPECTAMF:
                self.input.transactionStart()
                try:
                    self.readAMFPacket()
                except BufferedStringStreamInsufficientDataException:
                    self.input.transactionRollback()
                    return;
                self.input.transactionCommit()
                self.checkForFinishedAMFPackets()
    
    def readAMFPacket(self):
        firstbyte = self.input.readByte()
        headerlength = self.getHeaderSize(firstbyte)
        channelid = self.getchannelid(firstbyte)
        try:
            self.sChannel[channelid]
        except KeyError:
            self.sChannel[channelid] = {"data": "", "header": {}}
            self.sChannel[channelid]["header"]["channelid"] = channelid
        if headerlength >=4:
            self.sChannel[channelid]["header"]["timestamp"] = self.input.readUInt24B()
        if headerlength >=8:
            self.sChannel[channelid]["header"]["size"] = self.input.readUInt24B()
            self.sChannel[channelid]["header"]["kind"] = self.input.readByte()
        if headerlength >=12:
            self.sChannel[channelid]["header"]["src_dst"] = self.input.readUInt32()
        dataneeded = self.sChannel[channelid]["header"]["size"] - len(self.sChannel[channelid]["data"])
        self.sChannel[channelid]["data"]+=self.input.read(min(dataneeded, self.read_chunk_size))
    
    def checkForFinishedAMFPackets(self):
        for channelid in self.sChannel:
            if len(self.sChannel[channelid]["data"]) == self.sChannel[channelid]["header"]["size"]:
                self.handleAMFPacket(self.sChannel[channelid])
                self.sChannel[channelid]["data"] = ""
     
    def handleAMFPacket(self, amfpacket):
        if amfpacket["header"]["kind"] == RTMPProtocol.KIND_KCALL:
            logging.debug("Decoding call: \n%s"%getBinaryStream(amfpacket["data"]))
            input = cStringIO.StringIO(amfpacket["data"])
            callobject = {}
            type = amf0.read_byte(input)
            callobject["name"]=amf0.read_data(input, type, None)
            type = amf0.read_byte(input)
            callobject["id"]=int(amf0.read_data(input, type, None))
            callobject["argv"] = []
            while True:
                c = input.read(1)
                if c == "":
                    break
                type = ord(c)
		try:
	                callobject["argv"].append(amf0.read_data(input, type, None))
		except Exception: pass	#somehow flash from the IDE sends a parameter that we cannot parse
			
            logging.debug("Received a KCall %s (header %s)" %(repr(callobject), repr(amfpacket["header"])))
            try:
                remotecallable = self.remotecallables[callobject["name"]]
            except KeyError:
                raise RTMPProtocolUnknownRemoteCallableException("Received unknown remotecallable: %s"%callobject["name"])
            remotecallable(amfpacket["header"], callobject)
        elif amfpacket["header"]["kind"] == RTMPProtocol.KIND_KCOMMAND:
            logging.debug("Decoding command: \n%s"%getBinaryStream(amfpacket["data"]))
            input = rtmputil.FancyReader(BufferedStringStream())
            input.write(amfpacket["data"])
            commandkind = input.readUInt16B()
            streamid = input.readUInt32B()
            commandbodysize = RTMPProtocol.COMMANDSIZE[commandkind]
            assert commandbodysize == input.bytesAvailable(), "commandkind %d, bodysize, %d" % (commandkind, len(amfpacket["data"]))
            try:
                command = self.commands[commandkind]
            except KeyError:
                raise RTMPProtocolUnknownCommandException("Received unknown command: %d"%commandkind)
            command(streamid, input)
        elif amfpacket["header"]["kind"] == RTMPProtocol.KIND_KBYTESREADED:
            input = rtmputil.FancyReader(BufferedStringStream())
            input.write(amfpacket["data"])
            bytesreaded = input.readUInt32B()
            logging.debug("Bytes readed: %d"%bytesreaded)
        else:
            raise Exception ("Not sure what to do, unknown kind: 0x%02x"%amfpacket["header"]["kind"])
    
    def flushOutput(self):
        data = self.output.readAll()
#        logging.debug("Sending: \n%s"%getBinaryStream(data))
        self.transport.write(data)
        self.output.reset()
    
    def sendCommand(self, commandkind, streamid):
        stream = rtmputil.FancyWriter(BufferedStringStream())
        stream.writeUInt16B(commandkind);
        stream.writeUInt32B(streamid);

        channelid=2 # this seems always to be 2
        self.send(channelid=channelid, data=stream.readAll(), kind=RTMPProtocol.KIND_KCOMMAND, streamid=0) #streamid is 0 here, is already set in the command
    
    def sendFLVChunk(self, channelid, chunk, streamid, timestamp):
        if chunk.CHUNKTYPE == flv.FLVMetaDataChunk.CHUNKTYPE:
            logging.debug("Metadata, not sending")
            return;
#        logging.debug("Sending a %s, time %d, bytes %d"%(chunk.__class__.__name__, chunk.time, len(chunk.data)))
        self.send(channelid=channelid, data=chunk.data, kind=chunk.CHUNKTYPE, streamid=streamid, timestamp=timestamp)
    
    def sendCall(self, channelid, call, streamid=0):
        stream = cStringIO.StringIO()
        amf0.write_string(call["name"], stream)
        amf0.write_number(call["id"], stream)
        for arg in call["argv"]:
            amf0.write_data(arg, stream)
        self.send(channelid=channelid, data=stream.getvalue(), kind=RTMPProtocol.KIND_KCALL, streamid=streamid)
        
    def send(self, channelid, data, kind, streamid=0, timestamp=0):
        header = {
            "channelid": channelid,
            "timestamp": timestamp,
            "kind": kind,
            "src_dst": streamid,
            "size" : len(data)
        }
        self.writeHeader(header)
        headerbyte = self.getHeaderSingleByte(header)
        partitioneddata = chr(headerbyte).join(split_len(data, self.write_chunk_size))
        self.output.write(partitioneddata)
        self.flushOutput()
        
    def getHeaderSingleByte(self,header):
        headerlength = 1
        return header["channelid"] | (RTMPProtocol.HEADERSIZE.index(headerlength) << 6)
        
    
    def writeHeader(self, header ):
        if header["src_dst"] != None:
            headerlength = 12;
        elif header["kind"] != None:
            headerlength = 8;
        elif header["timestamp"] != None:
            headerlength = 4;
        else:
            headerlength = 1;
        self.output.writeByte(header["channelid"] | (RTMPProtocol.HEADERSIZE.index(headerlength) << 6))
        if headerlength >= 4:
            self.output.writeUInt24B(header["timestamp"]);
        if headerlength >= 8:
            self.output.writeUInt24B(header["size"]);
            self.output.writeByte(header["kind"]);
        if headerlength == 12:
            self.output.writeUInt32(header["src_dst"]);


    def readWelcomeHandshake(self):
        if self.input.readByte() != RTMPProtocol.WELCOMEBYTE:
            raise RTMPProtocolHandshakeException("Expected first handshake character to be 0x03")
        self.handshake = self.input.read(RTMPProtocol.HANDSHAKELENGTH)
    
    def replyToHandshake(self, includeWelcomeByte):
        if includeWelcomeByte:
            self.output.writeByte(RTMPProtocol.WELCOMEBYTE)    
        self.output.write(self.handshake)
        self.flushOutput()
    
    def readReplyHandshake(self,):
        handshake = self.input.read(RTMPProtocol.HANDSHAKELENGTH)
#        if not self.handshake == handshake:
#            logging.debug("handshake: \n%s"%getBinaryStream(self.handshake))
#            logging.debug("handshake2: \n%s"%getBinaryStream(handshake))
#            raise RTMPProtocolHandshakeException("Replyhandshake does not match initial handshake")
    
    def getHeaderSize(self, firstbyte):
        return RTMPProtocol.HEADERSIZE[firstbyte >> 6]

    def getchannelid(self, firstbyte):
        return firstbyte & 0x3F
    
    def getLastHeader(self, channelid):
        try:
            return self.sChannel[channelid]["lastheader"]
        except KeyError:
            return {
                    "channelid": channelid,
                    "timestamp": 0,
                    "size": None,
                    "src_dst": 0,
                    }
    
    def rpcConnect(self, header, callobject):
        logging.info("Connected: %s"%repr(callobject))
        call = {
                "name": "_result",
                "id": callobject["id"],
                "argv": [
                         None,
                         {
                          "level": "status",
                          "code": "NetConnection.Connect.Success",
                          "description": "Connection succeeded."
                         }
                        ]
                }
        self.sendCall(header["channelid"], call)
    
    def rpcCreateStream(self, header, callobject):
        streamid =1
        while True:
            try:
                self.sStream[streamid]
            except KeyError:
                break
            else:
                streamid+=1;
        self.sStream[streamid] = {
                                  "id": streamid,
                                  "channelid": None,
                                  "play": None,
                                  "record": None,
                                  "audio": True,
                                  "video": True,
                                 }
        call = {
                "name": "_result",
                "id": callobject["id"],
                "argv": [
                         None,
                         int(streamid),
                        ]
                }
        self.sendCall(header["channelid"], call)
        logging.info("Created stream with id: %d"%streamid)
    
    def rpcPlay(self, header, callobject):
        # TODO: add security for the file
        filename = callobject["argv"][1];
        logging.info("Requested file: %s"%filename)
        #for now :)
        filename = "/mnt/media/%s"%filename
        streamid = header["src_dst"]
        buffer = BufferedStringStream()
        processProtocol=ProcessProtocolBufferWriter(buffer);
        reactor.spawnProcess(processProtocol, 'convertvideo.sh', ['convertvideo.sh', filename])
        assert self.sStream[streamid]["play"] == None
        reader= flv.FLVReader(buffer);
        self.sStream[streamid]["channelid"]=header["channelid"]
        self.sStream[streamid]["play"]= {
                         "reader": reader,
                         "buffer": buffer,
                         "processProtocol": processProtocol,
                         "flv": None,
                         "starttime": time.time()-5,
                         "curTime": 0,
                         "blocked": None,
                         "paused": None,
                        };
        self.seek(streamid,0);
        call = {
                "name": "onStatus",
                "id": callobject["id"],
                "argv": [
                         None,
                         {
                          "level": "status",
                          "code": "NetStream.Play.Reset",
                          "description": "Resetting "+filename+".",
                          "details": filename,
                          "clientId": int(streamid),
                         }
                        ]
                }
        self.sendCall(header["channelid"], call, streamid=streamid)
        call2 = {
                "name": "onStatus",
                "id": callobject["id"],
                "argv": [
                         None,
                         {
                          "level": "status",
                          "code": "NetStream.Play.Start",
                          "description": "Start playing "+filename+".",
                          "clientId": int(streamid),
                         }
                        ]
                }
        self.sendCall(header["channelid"], call2, streamid=streamid)
        self.playFLV()
    
    def cmdClear(self, streamid, inputstream):
        logging.info("Received command clear (streamid: %d)"%streamid)
        
    def cmdPlay(self, streamid, inputstream):
        logging.info("Received command play (streamid: %d)"%streamid)
        
    def cmdClientBuffer(self, streamid, inputstream):
        logging.info("Received command clientbuffer (streamid: %d), param %d"%(streamid, inputstream.readUInt32B()))
        
    def cmdReset(self, streamid, inputstream):
        logging.info("Received command reset (streamid: %d)"%streamid)
        
    def cmdPing(self, streamid, inputstream):
        logging.info("Received command ping (streamid: %d), param %d"%(streamid, inputstream.readUInt32B()))
    
    def seek(self, streamid, timestamp):
        self.sendCommand(RTMPProtocol.COMMANDKIND_PLAY, streamid)
        self.sendCommand(RTMPProtocol.COMMANDKIND_RESET, streamid)
        self.sendCommand(RTMPProtocol.COMMANDKIND_CLEAR, streamid)
        self.playFLV()
#        for _ in range(3):
#            chunk = self.sStream[streamid]["play"]["reader"].readChunk()
#            self.sendFLVChunk(self.sStream[streamid]["channelid"], chunk, streamid, chunk.time)
            
    
    def playFLV(self):
        now = time.time()
        for streamid in self.sStream:
            if self.sStream[streamid]["play"]:
                logging.debug("Stream %d needs playing (%.3f sec)"%(streamid, now-self.sStream[streamid]["play"]["starttime"]))
                while True:
                    self.sStream[streamid]["play"]["buffer"].transactionStart()
                    try:
                        chunk = self.sStream[streamid]["play"]["reader"].readChunk()
                    except BufferedStringStreamInsufficientDataException:
                        self.sStream[streamid]["play"]["buffer"].transactionRollback()
                        if self.sStream[streamid]["play"]["processProtocol"].ended:
                            self.sStream[streamid]["play"]=None
                        logging.info("Breaking because not enough data available")
                        break
		    self.sStream[streamid]["play"]["buffer"].transactionCommit()
                        
                    self.sendFLVChunk(self.sStream[streamid]["channelid"], chunk, streamid, chunk.time)
                    if (float(chunk.time)/1000) + self.sStream[streamid]["play"]["starttime"] > now:
                        break;
                

def split_len(seq, length):
     return [seq[i:i+length] for i in range(0, len(seq), length)]
 
def getBinaryStream(str):
    PRINT_LENGTH=16
    s = []
    for i in range(0,len(str),PRINT_LENGTH):
        aChar = []
        aInt = []
        for j in range(i,min(i+PRINT_LENGTH, len(str))):
            if ord(str[j]) > 32 and ord(str[j]) < 128:
                aChar.append(str[j]);
            else :
                aChar.append(".");
            aInt.append(ord(str[j]));
        hextext = ("%02x "*len(aInt))%tuple(aInt);
        hextext = "  ".join(split_len(hextext,3*PRINT_LENGTH/2))
        hrtext = ("%s "*len(aInt))%tuple(aChar);
        hrtext = "  ".join(split_len(hrtext,2*PRINT_LENGTH/2))
        format = "%-"+("%d"%(3*PRINT_LENGTH+2))+"s        %s";
        s.append(("0x%04x  "+format)%(i, hextext, hrtext))
    return "\n".join(s)
    


class BufferedStringStream:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.buffer={"content":{},
                     "pointer": [0,0,0],
                     "bytesAvailable":0,
                     }
        self.bufferBeforeTransaction = []
        
    def read(self,bytes):
        if bytes > self.bytesAvailable():
            raise BufferedStringStreamInsufficientDataException()
        toread=int(bytes)
        readeddata = []
#        print(("start (%d): "%toread)+self.getStatus())
        while len(self.buffer["content"][self.buffer["pointer"][0]]) < self.buffer["pointer"][1]+toread:
            datachunk = self.buffer["content"][self.buffer["pointer"][0]][self.buffer["pointer"][1]:]
            toread -= len(datachunk)
            readeddata.append(datachunk)
#            self.buffer["content"][self.buffer["pointer"][0]] = None # clean up to save space
            self.buffer["pointer"][0] += 1
            self.buffer["pointer"][1] = 0
#            print(("looping (%d): "%toread)+self.getStatus())
        readeddata.append(self.buffer["content"][self.buffer["pointer"][0]][self.buffer["pointer"][1]:self.buffer["pointer"][1]+toread])
        self.buffer["pointer"][1] += toread
        toread=0
        self.buffer["bytesAvailable"] -= bytes
#        print(("done (%d): "%toread)+self.getStatus())
#        print("Requested %d data, got %d"%(bytes,len("".join(readeddata))))
        return "".join(readeddata)
    
    def readAll(self):
        return self.read(self.bytesAvailable())
    
    def transactionStart(self):
        self.bufferBeforeTransaction.append(copy.deepcopy((self.buffer["pointer"], self.buffer["bytesAvailable"])))
    
    def transactionCommit(self):
        if len(self.bufferBeforeTransaction) == 0:
            raise BufferedStringStreamTransactionException("Not in transaction")
        self.bufferBeforeTransaction.pop()
    
    def transactionRollback(self):
        if len(self.bufferBeforeTransaction) == 0:
            raise BufferedStringStreamTransactionException("Not in transaction")
        self.buffer["pointer"],self.buffer["bytesAvailable"] = self.bufferBeforeTransaction.pop()
    
    def bytesAvailable(self):
        return self.buffer["bytesAvailable"]
        
    def write(self, data):
        self.buffer["content"][self.buffer["pointer"][2]]=data
        self.buffer["pointer"][2]+=1
        self.buffer["bytesAvailable"] += len(data)
        
    def getStatus(self):
        s="pointers: "+repr(self.buffer["pointer"])+"\nbuffers: \n";
        for i in self.buffer["content"]:
            s+="  %d: %d\n"%(i, len(self.buffer["content"][i]))
        return s;
        
class BufferedStringStreamInsufficientDataException(Exception): pass
class BufferedStringStreamTransactionException(Exception): pass

class RTMPProtocolHandshakeException (Exception): pass
class RTMPProtocolUnknownCommandException (Exception): pass
class RTMPProtocolUnknownRemoteCallableException (Exception): pass

class BasicServerFactory(protocol.ServerFactory):
    protocol = RTMPProtocol

logging.basicConfig(level=logging.DEBUG)

#f=open("/tmp/amf","r")
#amfstring = f.read()
#f.close();

#test = RTMPProtocol()
#test.state = RTMPProtocol.STATE_EXPECTAMF
#test.dataReceived(amfstring)

reactor.listenTCP(1935, BasicServerFactory( ))
reactor.run( )
