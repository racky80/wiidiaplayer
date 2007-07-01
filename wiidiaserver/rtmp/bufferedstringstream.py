import logging, copy

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
