'''
RTMPy is available under the terms of the MIT license.  The full text
of the MIT license is included below.

MIT License
===========

Copyright (c) 2007 The RTMPy Project. All rights reserved.

Arnar Birgisson
Thijs Triemstra

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import logging, copy

class BufferedStringStream:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.buffer={"content":{},
                     "pointer": [0,0,0],
                     "bytesAvailable":0,
                     "bytesRead": 0
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
        self.buffer["bytesRead"]+=bytes
        return "".join(readeddata)
    
    def readAll(self):
        return self.read(self.bytesAvailable())
    
    def transactionStart(self):
        self.bufferBeforeTransaction.append(copy.deepcopy((self.buffer["pointer"], self.buffer["bytesAvailable"], self.buffer["bytesRead"])))
    
    def transactionCommit(self):
        if len(self.bufferBeforeTransaction) == 0:
            raise BufferedStringStreamTransactionException("Not in transaction")
        self.bufferBeforeTransaction.pop()
    
    def transactionRollback(self):
        if len(self.bufferBeforeTransaction) == 0:
            raise BufferedStringStreamTransactionException("Not in transaction")
        self.buffer["pointer"],self.buffer["bytesAvailable"],self.buffer["bytesRead"] = self.bufferBeforeTransaction.pop()
    
    def bytesAvailable(self):
        return self.buffer["bytesAvailable"]
        
    def bytesRead(self):
        return self.buffer["bytesRead"]
        
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
