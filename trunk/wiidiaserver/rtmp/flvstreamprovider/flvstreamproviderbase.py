
class FileFlvStreamProviderTemporarilyNoChunkException(Exception): pass
class FileFlvStreamProviderStreamEndedException(Exception): pass
    
class FlvStreamProvider:
    '''abstract class from which all stream providers derive'''
    
    @classmethod
    def getFlvStreamProvider(cls, resourcename):
        import convertableaudioflvstreamprovider, convertablevideoflvstreamprovider, fileflvstreamprovider
        
        cls.PREFERREDPROVIDERS=[
                            fileflvstreamprovider.FileFlvStreamProvider,
                            convertableaudioflvstreamprovider.ConvertableAudioFlvStreamProvider,
                            convertablevideoflvstreamprovider.ConvertableVideoFlvStreamProvider,
                            ]
        """retrieves a streamprovider object that will play this file or directory"""
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