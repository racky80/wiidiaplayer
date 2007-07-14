from flvstreamproviderbase import *
import util

class FileFlvStreamProvider (FlvStreamProvider):
    BUFFERFILL_CHUNCKSIZE = 102400;
    
    def __init__(self, resourcename):
        FlvStreamProvider.__init__(self,resourcename)
        self.file=open(self.getFileName(), "r")
        self.buffer=util.bufferedstringstream.BufferedStringStream()
        self.flvreader = util.flv.FLVReader(self.buffer)

    @classmethod
    def supportsresource(cls, resourcename):
        '''returns whether a provider can provide the given resource'''
        return True

    def seek(self, position):
        pass;
    
    def getFileName(self):
        return self.resourcename
    
    def fileIsComplete(self):
        """returns boolean whether the file is complete. In normal circumstances this is always true, but for files generated, this may be different"""
        return True
    
    def fillBuffer(self):
        bytes = self.file.read(FileFlvStreamProvider.BUFFERFILL_CHUNCKSIZE)
        if bytes=="":
            if self.fileIsComplete():
                raise FileFlvStreamProviderStreamEndedException()
            else:
                raise FileFlvStreamProviderTemporarilyNoChunkException()
        self.buffer.write(bytes)
    
    def getFLVChunk(self):
        while True:
            self.buffer.transactionStart();
            try:
                chunk = self.flvreader.readChunk()
            except util.bufferedstringstream.BufferedStringStreamInsufficientDataException:
                self.buffer.transactionRollback();
                self.fillBuffer()
                continue
            self.buffer.transactionCommit();
            return chunk;
