from flvstreamproviderbase import *
import util
import fileflvstreamprovider
import thread, os.path


import popen2, commands, logging

class ConvertableVideoFlvStreamProvider (fileflvstreamprovider.FileFlvStreamProvider):
    def __init__(self, resourcename):
        tmpfile = "/tmp/convertor.flv";
        commands.getoutput("rm %s; touch %s"%(commands.mkarg(tmpfile),commands.mkarg(tmpfile)))
        fileflvstreamprovider.FileFlvStreamProvider.__init__(self,resourcename)
        cmd = "sh %s/convertvideo.sh %s %s > /tmp/log 2> /tmp/log2" % (commands.mkarg(os.path.dirname(__file__)), commands.mkarg(resourcename), commands.mkarg(tmpfile))
        self.convertor=AsynchronousProgramExecuter(cmd)

    def getFileName(self):
        return "/tmp/convertor.flv"

    def fileIsComplete(self):
        return False;
    

    @classmethod
    def supportsresource(cls, resourcename):
        '''returns whether a provider can provide the given resource'''
        return True
        
class AsynchronousProgramExecuter:
    def __init__(self, cmd, autostart=True):
        self.__cmd = cmd
        self.__started=False
        self.__output=[]
        self.__hasfinished = False;
        self.__outputpointer=0
        if autostart:
            self.start()

    def start(self):
        if self.__started:
            raise "Program already started"
        import popen2
        logging.debug("Now starting asynchronous program: %s" %self.__cmd)
        self.__p = popen2.Popen4(self.__cmd)
        self.__started = True
        thread.start_new_thread(self.__waitforprocess,())


    def __waitforprocess(self):
        for line in self.__p.fromchild:
            self.__output.append(line)
        self.__result = self.__p.poll()
        self.__hasfinished = True

    def hasfinished(self):
        return self.__hasfinished

    def getresult(self):
        if not self.hasfinished():
            raise "Process not finished yet"
        return self.__result

    def getoutput(self):
        if not self.hasfinished():
            raise "Process not finished yet"
        return "".join(self.__output)

    def getprogressiveoutput(self):
        '''
          gets the output up to the point we are now, since the last time this function was called
        '''
        oldoutputpointer=self.__outputpointer
        self.__outputpointer = len(self.__output)
        return "".join(self.__output[oldoutputpointer:self.__outputpointer])


    def getcommand(self):
        return self.__cmd


