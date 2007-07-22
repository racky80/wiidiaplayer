from flvstreamproviderbase import *
import util
import os.path, logging

class FileFlvStreamProvider (FlvStreamProvider):
    BUFFERFILL_CHUNCKSIZE = 102400;
    
    def __init__(self, resourcename):
        FlvStreamProvider.__init__(self,resourcename)
        self.file=open(self.getFileName(), "r")
        self.aKeyFrame = []
        self.maxtimestamp=0
        self.seekStatus = None

    @classmethod
    def supportsresource(cls, resourcename):
        '''returns whether a provider can provide the given resource'''
        return resourcename.split(".")[-1] == "flv";

    def getFileName(self):
        return self.resourcename
    
    def fileIsComplete(self):
        """returns boolean whether the file is complete. In normal circumstances this is always true, but for files generated, this may be different"""
        return True
    
    def seek(self, timestamp):
        if timestamp == 0:
            self.buffer=util.bufferedstringstream.BufferedStringStream()
            self.flvreader = util.flv.FLVReader(self.buffer)
            self.seekFile(0)
            self.seekStatus = None
        else:
            self.seekStatus = { "starttmaxtimestamp": None, # we'll fill this in later after we catch up
                                "timestamp": timestamp,
                                "videosync": False,
                                "audiosync": False,
                                "filesync": False,
                               }

    def hasVideo(self):
        return True
    
    def seekFile(self, filepos):
        self.buffer.reset()
        self.file.seek(filepos)
        self.fileposoffset = filepos

    def __del__(self):
        logging.info("stream deleted")

    
    def fillBuffer(self):
        bytes = self.file.read(FileFlvStreamProvider.BUFFERFILL_CHUNCKSIZE)
        if len(bytes)==0:
            if self.fileIsComplete():
                raise FileFlvStreamProviderStreamEndedException()
            else:
                if self.seekStatus:
                    if self.seekStatus["starttmaxtimestamp"] == None:
                        self.seekStatus["starttmaxtimestamp"] = self.maxtimestamp
                    raise FileFlvStreamProviderTemporarilyNoChunkException(self.seekStatus["starttmaxtimestamp"], self.maxtimestamp, self.seekStatus["timestamp"])
                else:
                    #normal starting situation
                    raise FileFlvStreamProviderTemporarilyNoChunkException(0, 0, 0)
        self.buffer.write(bytes)
    
    def getFLVChunk(self):
        seeking = False
        if self.seekStatus and not self.seekStatus["filesync"]:
            if len(self.aKeyFrame) and self.seekStatus["timestamp"] <= self.aKeyFrame[-1]["timestamp"]:
                for i in range(len(self.aKeyFrame))[::-1]:
                    if self.aKeyFrame[i]["timestamp"] <= self.seekStatus["timestamp"]:
                        self.seekFile(self.aKeyFrame[i]["filepos"])
                        self.seekStatus["filesync"] = True
                        break;
            else:
                seeking=True
                    
        self.buffer.transactionStart();
        try:
            pos = self.buffer.bytesRead()+self.fileposoffset;
            chunk = self.flvreader.readChunk()
        except util.bufferedstringstream.BufferedStringStreamInsufficientDataException:
            self.buffer.transactionRollback();
            try:
                self.fillBuffer()
            except FileFlvStreamProviderStreamEndedException:
                if seeking:
                    timestamp = self.aKeyFrame[-1]["timestamp"]-1000;
                    logging.info("seeking over the end of the file, retrying seek 1 secs before the last keyframe: %d"%timestamp)
                    self.seek(timestamp)
                    return self.getFLVChunk();
                else:
                    raise
            return self.getFLVChunk()
        self.maxtimestamp = max(self.maxtimestamp, chunk.time)
            
        self.buffer.transactionCommit();
        
        if (chunk.CHUNKTYPE == util.flv.FLVVideoChunk.CHUNKTYPE and chunk.isKeyFrame) or not self.hasVideo(): # if we don;t have video, every frame is a keyframe
            if len(self.aKeyFrame) == 0 or chunk.time > self.aKeyFrame[-1]["timestamp"]: #we might be replaying a part we checkout out before, make sure that the timestamps stay in order
                self.aKeyFrame.append({"timestamp":chunk.time, "filepos":pos})
        
        if seeking:
            if self.seekStatus["timestamp"] < chunk.time:
                self.seekFile(self.aKeyFrame[-1]["filepos"])
                self.seekStatus["filesync"] = True
            return None
        
        if self.seekStatus:
            if chunk.CHUNKTYPE == util.flv.FLVMetaDataChunk.CHUNKTYPE:
                return None
            if chunk.CHUNKTYPE == util.flv.FLVAudioChunk.CHUNKTYPE:
                if chunk.time < self.seekStatus["timestamp"]:
                    return None
                else:
                    if not self.seekStatus["audiosync"]:
                        chunk.time=0;
                        self.seekStatus["audiosync"] = True
            if chunk.CHUNKTYPE == util.flv.FLVVideoChunk.CHUNKTYPE:
                if chunk.time < self.seekStatus["timestamp"]:
                    chunk.time=0;
                else:
                    if not self.seekStatus["videosync"]:
                        chunk.time=0;
                        self.seekStatus["videosync"] = True
            if (self.seekStatus["videosync"] or not self.hasVideo()) and self.seekStatus["audiosync"]:
                self.seekStatus = None
        
        return chunk;
