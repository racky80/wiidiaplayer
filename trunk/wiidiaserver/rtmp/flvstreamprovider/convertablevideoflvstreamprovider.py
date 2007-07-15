import convertableflvstreamprovider
import os.path

class ConvertableVideoFlvStreamProvider (convertableflvstreamprovider.ConvertableFlvStreamProvider):
    def __init__(self, resourcename):
        convertableflvstreamprovider.ConvertableFlvStreamProvider.__init__(self,resourcename)

    def getShellConvertingScript(self):
        return "%s/convertvideo.sh"% os.path.dirname(__file__)

    @classmethod
    def supportsresource(cls, resourcename):
        '''returns whether a provider can provide the given resource'''
        return True # we'll just return true until we have a better plan (not by extention I would think....
        return resourcename.split(".")[-1] in ("avi", "mpeg", "mpg", "wmv");
        
