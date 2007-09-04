from flvstreamproviderbase import *
import util
import os.path, logging, commands

class FileFlvStreamProvider (FlvStreamProvider):
    BUFFERFILL_CHUNCKSIZE = 102400;
    
    def __init__(self, resourcename):
        FlvStreamProvider.__init__(self,resourcename)
        self.playfile=open(self.getFileName(), "r")
        self.seekfile=open(self.getFileName(), "r")
        self.seekbuffer = util.bufferedstringstream.BufferedStringStream()
        self.flvseeker = util.flv.FLVReader(self.seekbuffer)
        self.aKeyFrame = [{"timestamp":0, "filepos":0}]
        self.maxtimestamp=0
        self.medialength=int(float(commands.getoutput("sh %s/medialength.sh %s"%(commands.mkarg(os.path.dirname(__file__)), commands.mkarg(resourcename))))*1000)
        self.seekStatus = None
        self.lasttimestamp=0;

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
        if filepos == 0:
            self.buffer=util.bufferedstringstream.BufferedStringStream()
            self.flvreader = util.flv.FLVReader(self.buffer)
        else:
            self.buffer.reset()
            self.playfile.seek(filepos)

    def __del__(self):
        logging.info("stream deleted")
        
    
    def buildSeekIndex(self):
        """Reads some of the file, and builds the searchindex from it. Ideally, this would always read all the way to the end of the file, and keeps up with rendering (if rendering)"""
        runs = 0;
        while runs < 100:
            runs += 1
            bytes = self.seekfile.read(FileFlvStreamProvider.BUFFERFILL_CHUNCKSIZE)
            if len(bytes)==0:
                # either the file is finished, or the file is still rendering, either way, nothing to do
                return
            else:
                self.seekbuffer.write(bytes)
            while True:
                self.seekbuffer.transactionStart();
                try:
                    pos = self.seekbuffer.bytesRead();
                    chunk = self.flvseeker.readChunk()
                except util.bufferedstringstream.BufferedStringStreamInsufficientDataException:
                    self.seekbuffer.transactionRollback();
                    break
                self.seekbuffer.transactionCommit();
                self.maxtimestamp = max(chunk.time, self.maxtimestamp)
                if (chunk.CHUNKTYPE == util.flv.FLVVideoChunk.CHUNKTYPE and chunk.isKeyFrame) or not self.hasVideo(): # if we don't have video, every frame is a keyframe
                    if len(self.aKeyFrame) == 0 or chunk.time > self.aKeyFrame[-1]["timestamp"]+200: #we might be replaying a part we checkout out before, make sure that the timestamps stay in order; in addition, we store at most 5 timestamps per second, to save memory
                        self.aKeyFrame.append({"timestamp":chunk.time, "filepos":pos})
            if len(bytes) < FileFlvStreamProvider.BUFFERFILL_CHUNCKSIZE:
                return
            
    def getMediaInfo(self):
        return {"totallength": self.medialength, "availablelength": self.maxtimestamp}

    def fillBuffer(self):
        bytes = self.playfile.read(FileFlvStreamProvider.BUFFERFILL_CHUNCKSIZE)
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
        self.buildSeekIndex()

        if self.seekStatus and not self.seekStatus["filesync"]: # we are trying to find the file position 
            if self.seekStatus["timestamp"] > self.maxtimestamp:
                return None
            for i in range(len(self.aKeyFrame))[::-1]:
                if self.aKeyFrame[i]["timestamp"] <= self.seekStatus["timestamp"]:
                    self.seekFile(self.aKeyFrame[i]["filepos"])
                    self.seekStatus["filesync"] = True
                    break;
        
        self.buffer.transactionStart();
        try:
            chunk = self.flvreader.readChunk()
        except util.bufferedstringstream.BufferedStringStreamInsufficientDataException:
            self.buffer.transactionRollback();
            self.fillBuffer()
            return self.getFLVChunk()
            
        self.buffer.transactionCommit();
        
        if self.seekStatus:
            if chunk.CHUNKTYPE == util.flv.FLVMetaDataChunk.CHUNKTYPE:
                return None
            if chunk.CHUNKTYPE == util.flv.FLVAudioChunk.CHUNKTYPE:
                if chunk.time < self.seekStatus["timestamp"]:
                    chunk = self.getFLVChunk()
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
                self.seekStatus = None #done seeking
        
        return chunk;
