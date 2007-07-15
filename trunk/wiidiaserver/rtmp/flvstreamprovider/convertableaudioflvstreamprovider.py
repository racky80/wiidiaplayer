import convertableflvstreamprovider
import os.path

class ConvertableAudioFlvStreamProvider (convertableflvstreamprovider.ConvertableFlvStreamProvider):
    def __init__(self, resourcename):
        convertableflvstreamprovider.ConvertableFlvStreamProvider.__init__(self,resourcename)

    def getShellConvertingScript(self):
        return "%s/convertaudio.sh"% os.path.dirname(__file__)

    @classmethod
    def supportsresource(cls, resourcename):
        '''returns whether a provider can provide the given resource'''
        return resourcename.split(".")[-1] in ("mp3", "ogg", "wav");
        
    def hasVideo(self):
        return False
