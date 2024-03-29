
class FileFlvStreamProviderTemporarilyNoChunkException(Exception):
    def __init__(self, starttimestamp, currenttimestamp, targettimestamp):
        self.starttimestamp = starttimestamp
        self.currenttimestamp = currenttimestamp
        self.targettimestamp = targettimestamp
    
class FileFlvStreamProviderStreamEndedException(Exception): pass
class FileFlvStreamProviderStreamErrorException(Exception): pass
    
class FlvStreamProvider:
    '''abstract class from which all stream providers derive'''
    
    @classmethod
    def getFlvStreamProvider(cls, resourcename):
        """retrieves a streamprovider object that will play this file or directory"""
        import convertableaudioflvstreamprovider, convertablevideoflvstreamprovider, convertableffmpegvideoflvstreamprovider, fileflvstreamprovider
        
        cls.PREFERREDPROVIDERS=[
                            fileflvstreamprovider.FileFlvStreamProvider,
                            convertableaudioflvstreamprovider.ConvertableAudioFlvStreamProvider,
#                            convertableffmpegvideoflvstreamprovider.ConvertableFFMpegVideoFlvStreamProvider,
                            convertablevideoflvstreamprovider.ConvertableVideoFlvStreamProvider,
                            ]
        for provider in FlvStreamProvider.PREFERREDPROVIDERS:
            if provider.supportsresource(resourcename):
                return provider(resourcename)
        raise NoCompatibleStreamProviderException();
    
    def __init__(self, resourcename):
        '''creates a new provider for the given resource'''
        if not self.supportsresource(resourcename):
            raise UnsupportedResourceForStreamProviderException()
        self.resourcename = resourcename
        self.buffertime=5
        
    @classmethod
    def supportsresource(cls, resourcename):
        '''returns whether a provider can provide the given resource'''
        return False
    
    def play(self):
        self.seek(0)
        
    def seek(self, position):
        '''seeks to the specified second in the stream
        returns true if seek is supported and possible'''
        return False
    
    def __del__(self):
        '''cleans up the stream'''
        pass
    
    def getFLVChunk(self):
        '''gets a FLVchunk, or '''
        pass

class UnsupportedResourceForStreamProviderException(Exception): pass
class NoCompatibleStreamProviderException(Exception): pass
class TemporarStreamProviderException(Exception): pass