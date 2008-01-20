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
 
def checkPath(path):
    import os
    """checks to see that a path is a real absolute path"""
    return path == os.path.realpath(path)