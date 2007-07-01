import rtmputil

class FLVChunk:
    def __init__(self, data, time):
        self.data = data
        self.time = time

class FLVAudioChunk(FLVChunk):
    CHUNKTYPE=0x08

class FLVVideoChunk(FLVChunk):
    CHUNKTYPE=0x09
    def isKeyFrame(self):
        return (ord(self.data[0]) >> 4) == 1

class FLVMetaDataChunk(FLVChunk):
    CHUNKTYPE=0x12

class FLVReader:
    CHUNKTYPE = {
                 FLVAudioChunk.CHUNKTYPE: FLVAudioChunk,
                 FLVVideoChunk.CHUNKTYPE: FLVVideoChunk,
                 FLVMetaDataChunk.CHUNKTYPE: FLVMetaDataChunk,
                 }
    
    def __init__(self, readableobject):
        self.input=rtmputil.FancyReader(readableobject)
        self.headerReaded=False
        
    def readHeader(self):
        r = self.input.read(3)
        assert r == "FLV", "Signature"
        r = self.input.readByte()
        assert r == 0x01, "FLV version"
        flags = self.input.readByte()
        #apparently the flags are not ok for mencoder material
#        assert flags == 0x05 or flags == 0x01, "Type flags"
        r = self.input.readUInt32B()
        assert r == 0x09, "offset"
        r = self.input.readUInt32B()
        assert r == 0x00, "prev (whatever that may be)"
        
    def readChunk(self):
        if not self.headerReaded:
            self.readHeader()
        chunktype = self.input.readByte()
        size = self.input.readUInt24B()
        time = self.input.readUInt24B()
        r = self.input.readUInt32B()
        #apparently the reserved bits are not ok for mencoder material
#        assert r == 0x00, "Reserved bits"
        data = self.input.read(size)
        size2 = self.input.readUInt32B()
        assert size2 == 0 or size2 == size+11, "Second size doesn't agree"
        
        self.headerReaded = True # we can only do this now because earlier the transaction could have been rolled back
        return FLVReader.CHUNKTYPE[chunktype](data, time)
        
class FLVWriter:
    def __init__(self, writeableobject):
        self.output=rtmputil.FancyWriter(writeableobject)
        
    def writeHeader(self):
        self.output.write("FLV");
        self.output.writeByte(0x01);
        self.output.writeByte(0x05);
        self.output.writeUInt32B(0x09);
        self.output.writeUInt32B(0x00);
    
    def writeChunk(self, chunk):
        self.output.writeByte(chunk.CHUNKTYPE)
        self.output.writeUInt24B(chunk.data.length);
        self.output.writeUInt24B(chunk.time);
        self.output.writeUInt32B(0);
        self.output.write(chunk.data);
        self.output.writeUInt32B(chunk.data.length + 11);


if __name__ == "__main__":
    import sys
    filename = sys.argv[1]
    print("Opening %s"%filename)
    file = open(filename)
    reader = FLVReader(file)
    header = reader.readHeader()
    while True:
        chunk = reader.readChunk()
        print("Read a %s, time %d, bytes %d"%(chunk.__class__.__name__, chunk.time, len(chunk.data)))