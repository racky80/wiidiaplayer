class FancyReader:
    def __init__(self, readableobject):
        if not callable(readableobject.read):
            raise FancyReaderNoReadMethodException()
        self.readableobject = readableobject
    
    def __getattr__(self, arg):
        return eval("self.readableobject.%s"%arg)

    def byteStringToInt(self, bytes):
        sum = 0;
        p = len(bytes)-1;
        for b in bytes:
            sum |= ord(b)<<(8*p)
            p-=1
        return sum
    
    def readByte(self):
        return self.readUInt8B()
    
    def readUInt8B(self):
        return self.byteStringToInt(self.read(1))
    
    def readUInt16B(self):
        return self.byteStringToInt(self.read(2))
    
    def readUInt24B(self):
        return self.byteStringToInt(self.read(3))
    
    def readUInt32B(self):
        return self.byteStringToInt(self.read(4))
        
    def readUInt32(self):
        return self.byteStringToInt(self.read(4)[::-1])

class FancyWriter:
    def __init__(self, writeableobject):
        if not callable(writeableobject.write):
            raise FancyWriterNoWriteMethodException()
        self.writeableobject = writeableobject
    
    def __getattr__(self, arg):
        return eval("self.writeableobject.%s"%arg)


    def intToByteString(self, num, length):
        result = []
        for p in range(length-1, -1, -1):
            result.append(chr((num >> (8*p)) & 0xff))
        return "".join(result)


    def writeByte(self, byte):
        return self.writeUInt8B(byte)
    
    def writeUInt8B(self, num):
        self.write(self.intToByteString(num,1))

    def writeUInt16B(self, num):
        self.write(self.intToByteString(num,2))

    def writeUInt24B(self, num):
        self.write(self.intToByteString(num,3))
    
    def writeUInt32B(self, num):
        self.write(self.intToByteString(num,4))
    
    def writeUInt32(self, num):
        self.write(self.intToByteString(num,4)[::-1])
    
class FancyReaderNoReadMethodException(Exception): pass
class FancyWriterNoWriteMethodException(Exception): pass
