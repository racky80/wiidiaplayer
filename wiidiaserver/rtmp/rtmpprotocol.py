import cStringIO
import logging, time, os
from twisted.internet import reactor, protocol, task
import util.amf
import util.amfutil
from amf import amf0
import pyamf
import util
import flvstreamprovider

class RTMPProtocol(protocol.Protocol):
    CLIENT_BUFFERLENGTH_SECONDS=5
    FLV_CHUNKSEND_INTERVAL_SECONDS=.5
    
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
        self.input = util.general.FancyReader(util.bufferedstringstream.BufferedStringStream())
        self.output = util.general.FancyWriter(util.bufferedstringstream.BufferedStringStream())
        self.sChannel = {}
        self.read_chunk_size=128
        self.write_chunk_size=128
        self.sStream={}
        self.remotecallables= {
                        "connect": self.rpcConnect,
                        "createStream": self.rpcCreateStream,
                        "play": self.rpcPlay,
                        "deleteStream": self.rpcDeleteStream,
                        "pause": self.rpcPause,
                        "seek": self.rpcSeek,
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
        self.playflv = task.LoopingCall(self.playFLV)
        self.playflv.start(RTMPProtocol.FLV_CHUNKSEND_INTERVAL_SECONDS)
        
    def connectionLost(self, reason):
        logging.info("Lost connection to %s." % self.transport.getPeer( ).host);
        self.playflv.stop();
        del(self.sStream);
        
    def dataReceived(self, data):
        logging.debug("Received: \n%s"%util.general.getBinaryStream(data))
        self.input.write(data)
        self.checkForParsableContent()
        
    def checkForParsableContent(self):
        while True:
            print "."
            if self.state == RTMPProtocol.STATE_WAITINGFORHANDSHAKE:
                self.input.transactionStart()
                try:
                    self.readWelcomeHandshake()
                except util.bufferedstringstream.BufferedStringStreamInsufficientDataException:
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
                except util.bufferedstringstream.BufferedStringStreamInsufficientDataException:
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
                except util.bufferedstringstream.BufferedStringStreamInsufficientDataException:
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
            logging.debug("Decoding call: \n%s"%util.general.getBinaryStream(amfpacket["data"]))
            input = pyamf.util.BufferedByteStream(amfpacket["data"])
            decoder = pyamf.decode(input)
            callobject = {}
            
            callobject["name"]=decoder.next()
            callobject["id"]=decoder.next()
            callobject["argv"] = list(decoder)
			
            logging.debug("Received a KCall %s (header %s)" %(repr(callobject), repr(amfpacket["header"])))
            try:
                remotecallable = self.remotecallables[callobject["name"]]
            except KeyError:
                raise RTMPProtocolUnknownRemoteCallableException("Received unknown remotecallable: %s"%callobject["name"])
            remotecallable(amfpacket["header"], callobject)
        elif amfpacket["header"]["kind"] == RTMPProtocol.KIND_KCOMMAND:
            logging.debug("Decoding command: \n%s"%util.general.getBinaryStream(amfpacket["data"]))
            input = util.general.FancyReader(util.bufferedstringstream.BufferedStringStream())
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
            input = util.general.FancyReader(util.bufferedstringstream.BufferedStringStream())
            input.write(amfpacket["data"])
            bytesreaded = input.readUInt32B()
            logging.debug("Bytes readed: %d"%bytesreaded)
        else:
            raise Exception ("Not sure what to do, unknown kind: 0x%02x"%amfpacket["header"]["kind"])
    
    def flushOutput(self):
        data = self.output.readAll()
#        logging.debug("Sending: \n%s"%util.general.getBinaryStream(data))
        self.transport.write(data)
        self.output.reset()
    
    def sendCommand(self, commandkind, streamid):
        stream = util.general.FancyWriter(util.bufferedstringstream.BufferedStringStream())
        stream.writeUInt16B(commandkind);
        stream.writeUInt32B(streamid);

        channelid=2 # this seems always to be 2
        self.send(channelid=channelid, data=stream.readAll(), kind=RTMPProtocol.KIND_KCOMMAND, streamid=0) #streamid is 0 here, is already set in the command
    
    def sendFLVChunk(self, channelid, chunk, streamid, timestamp):
        if chunk.CHUNKTYPE == util.flv.FLVMetaDataChunk.CHUNKTYPE:
            logging.debug("Metadata, not sending")
            return;
#        logging.debug("Sending a %s, time %d, bytes %d"%(chunk.__class__.__name__, chunk.time, len(chunk.data)))
        self.send(channelid=channelid, data=chunk.data, kind=chunk.CHUNKTYPE, streamid=streamid, timestamp=timestamp)
    
    def sendCall(self, channelid, call, streamid=0):
        stream = cStringIO.StringIO()
        stream.write(pyamf.encode(call["name"]).getvalue());
        stream.write(pyamf.encode(call["id"]).getvalue());
        for arg in call["argv"]:
            stream.write(pyamf.encode(arg).getvalue())
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
        partitioneddata = chr(headerbyte).join(util.general.split_len(data, self.write_chunk_size))
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
#            logging.debug("handshake: \n%s"%util.general.getBinaryStream(self.handshake))
#            logging.debug("handshake2: \n%s"%util.general.getBinaryStream(handshake))
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
        logging.info("createStream: %s"%(callobject.__repr__()))
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
    
    def rpcDeleteStream(self, header, callobject):
        logging.info("deleteStream: %s"%(callobject.__repr__()))
        streamid = header["src_dst"]
        if streamid == 0: # I assume  a streamid of 0 mean all streams (seems to get sent when player closes)
            self.sStream = {}
        else:
            del(self.sStream[streamid])
        
    
    def rpcPause(self, header, callobject):
        logging.info("Pause: %s"%(callobject.__repr__()))
        streamid = header["src_dst"]
        pause = callobject["argv"][1];
        time = callobject["argv"][2];
        
        if not self.sStream[streamid]["play"]:
            return
        
        if pause == None:
            pause = not self.sStream[streamid]["play"]["paused"];
        
        if pause:
            self.sStream[streamid]["play"]["paused"] = True;
            self.sendCommand(streamid, RTMPProtocol.COMMANDKIND_PLAY)
        else:
            self.sStream[streamid]["play"]["paused"] = False;
            self.seek(streamid, time)
        
        
        call = {
                "name": "_result",
                "id": callobject["id"],
                "argv": [
                         None,
                         {
                          "level": "status",
                          "code": {False: "NetStream.Unpause.Notify", True: "NetStream.Pause.Notify"}[self.sStream[streamid]["play"]["paused"]],
                         }
                        ]
                }
        self.sendCall(header["channelid"], call, streamid=streamid)
    
    def rpcPlay(self, header, callobject):
        logging.info("Play: %s"%(callobject.__repr__()))
        filename = callobject["argv"][1];
        logging.info("Requested file: %s"%filename)
        filename = "/mnt/media/%s"%filename
        if not os.path.isabs(filename):
            raise Exception("Not an absolute filename: %s"%filename)
        streamid = header["src_dst"]
        if self.sStream[streamid]["play"] != None: pass # the destructor will be called as soon as it's getting replaced
            
        self.sStream[streamid]["channelid"]=header["channelid"]
        self.sStream[streamid]["play"]= {
                         "provider": flvstreamprovider.FlvStreamProvider.getFlvStreamProvider(filename),
                         "starttime": None,
                         "paused": False,
                         "channelid": header["channelid"],
                         "ended": False,
                         "playstartsent": False,
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
        self.playFLV()
    
    def rpcSeek(self, header, callobject):
        logging.info("Seek: %s"%(callobject.__repr__()))
        streamid = header["src_dst"]
        time = max(callobject["argv"][1],0);
        self.seek(streamid, time)
        call = {
                "name": "_result",
                "id": callobject["id"],
                "argv": [
                         None,
                         {
                          "level": "status",
                          "code": "NetStream.Seek.Notify",
                         }
                        ]
                }
        self.sendCall(header["channelid"], call, streamid=streamid)
        if self.sStream[streamid]["play"]:
            self.sStream[streamid]["play"]["playstartsent"]=False

    
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
        try:
            if not self.sStream[streamid]["play"]:
                logging.info("Stream not playing, ignoring seek")
                return
        except KeyError:
            logging.info("Cannot find stream, ignoring seek")
            return
        self.sStream[streamid]["play"]["ended"] = False # we assume for now, will be set to True if it;s past the end
        self.sendCommand(RTMPProtocol.COMMANDKIND_PLAY, streamid)
        self.sendCommand(RTMPProtocol.COMMANDKIND_RESET, streamid)
        self.sendCommand(RTMPProtocol.COMMANDKIND_CLEAR, streamid)
        self.sStream[streamid]["play"]["starttime"] = None
        self.sStream[streamid]["play"]["provider"].seek(timestamp)
        self.playFLV()
#        for _ in range(3):
#            chunk = self.sStream[streamid]["play"]["reader"].readChunk()
#            self.sendFLVChunk(self.sStream[streamid]["channelid"], chunk, streamid, chunk.time)
            
    
    def playFLV(self):
        now = time.time()*1000
        chunks_sent=0;
        for streamid in self.sStream:
            if self.sStream[streamid]["play"] and not self.sStream[streamid]["play"]["ended"]:
                if self.sStream[streamid]["play"]["paused"]:
                    self.sStream[streamid]["play"]["provider"].buildSeekIndex()
                else:
                    firsttimestamp = 0;
                    while True:
                        try:
                            chunk = self.sStream[streamid]["play"]["provider"].getFLVChunk()
                        except flvstreamprovider.FileFlvStreamProviderTemporarilyNoChunkException, e:
                            logging.info("Breaking because not enough data available (sent %d chunks); (start: %d, current: %d, target: %d)"%(chunks_sent, e.starttimestamp, e.currenttimestamp, e.targettimestamp))
                            break;
                        except flvstreamprovider.FileFlvStreamProviderStreamEndedException:
                            logging.info("Breaking and stopping playback because stream ended (sent %d chunks)"%chunks_sent)
                            self.sStream[streamid]["play"]["ended"] = True;
                            call = {
                                    "name": "onStatus",
                                    "id": 0,
                                    "argv": [
                                             None,
                                             {
                                              "level": "status",
                                              "code": "NetStream.Buffer.Flush",
                                             }
                                            ]
                                    }
                            self.sendCall(self.sStream[streamid]["channelid"], call, streamid=streamid)
                            break;
                        except flvstreamprovider.FileFlvStreamProviderStreamErrorException:
                            logging.info("Breaking and stopping playback because stream error (sent %d chunks)"%chunks_sent)
                            self.sStream[streamid]["play"]["ended"] = True;
                            call = {
                                    "name": "onStatus",
                                    "id": 0,
                                    "argv": [
                                             None,
                                             {
                                              "level": "status",
                                              "code": "NetStream.Error",
                                             }
                                            ]
                                    }
                            self.sendCall(self.sStream[streamid]["channelid"], call, streamid=streamid)
                            break;
                        if chunk == None:
                            # the chunk available is not for sending
                            logging.info("Breaking because we're waiting for right chunk to become available")
                            break
                        
                        if not self.sStream[streamid]["play"]["playstartsent"]:
                            logging.info("Sending playstart")
                            call = {
                                    "name": "onStatus",
                                    "id": 0,
                                    "argv": [
                                             None,
                                             {
                                              "level": "status",
                                              "code": "NetStream.Play.Start",
                                             }
                                            ]
                                    }
                            self.sendCall(self.sStream[streamid]["channelid"], call, streamid=streamid)
                            self.sStream[streamid]["play"]["playstartsent"]=True
    
                        self.sendFLVChunk(self.sStream[streamid]["channelid"], chunk, streamid, chunk.time)
                        chunks_sent +=1
                        if firsttimestamp == 0: #note - after seeking timestamps of 0 are sent, so we ignore them
                            firsttimestamp = chunk.time
                        
                        if chunk.time > firsttimestamp + RTMPProtocol.FLV_CHUNKSEND_INTERVAL_SECONDS*1500:
                            logging.info("Breaking because we've sent 1.5 times the send interval (sent %d chunks)"%chunks_sent)
                            break;
                        if self.sStream[streamid]["play"]["starttime"] == None and chunk.time > 0:    # reset the starttime after a seek (which may take longer than intended)
                            self.sStream[streamid]["play"]["starttime"] = time.time()*1000-chunk.time - RTMPProtocol.CLIENT_BUFFERLENGTH_SECONDS*1000
                        if self.sStream[streamid]["play"]["starttime"] != None and chunk.time + self.sStream[streamid]["play"]["starttime"] > now:
                            logging.info("Breaking because we're up to date (sent %d chunks)"%chunks_sent)
                            break;
                mediainfo = self.sStream[streamid]["play"]["provider"].getMediaInfo()
                call = {
                        "name": "onStatus",
                        "id": 0,
                        "argv": [
                                 None,
                                 {
                                  "level": "status",
                                  "code": "Server.Media.Info",
                                  "totallength": mediainfo["totallength"]/1000,
                                  "availablelength": mediainfo["availablelength"]/1000,
                                 }
                                ]
                        }
                self.sendCall(self.sStream[streamid]["channelid"], call, streamid=streamid)
                

   



class RTMPProtocolHandshakeException (Exception): pass
class RTMPProtocolUnknownCommandException (Exception): pass
class RTMPProtocolUnknownRemoteCallableException (Exception): pass
