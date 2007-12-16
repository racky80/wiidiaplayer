import convertableflvstreamprovider
import os.path, commands

class ConvertableFFMpegVideoFlvStreamProvider (convertableflvstreamprovider.ConvertableFlvStreamProvider):
    def __init__(self, resourcename):
        convertableflvstreamprovider.ConvertableFlvStreamProvider.__init__(self,resourcename)
        print "using ffmpeg";

    def getShellConvertingScript(self):
        return "%s/convertvideoffmpeg.sh"% os.path.dirname(__file__)

    @classmethod
    def supportsresource(cls, resourcename):
        '''returns whether a provider can provide the given resource'''
        vcodec = commands.getoutput("sh %s/videocodec.sh %s"%(commands.mkarg(os.path.dirname(__file__)), commands.mkarg(resourcename)))
        return vcodec[0:2] == 'ff'
        
