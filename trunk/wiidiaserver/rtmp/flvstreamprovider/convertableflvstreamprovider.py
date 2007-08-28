from flvstreamproviderbase import *
import util
import util.asynchronousprogramexecuter
import fileflvstreamprovider
import os, os.path, random


import popen2, commands, logging

class ConvertableFlvStreamProvider (fileflvstreamprovider.FileFlvStreamProvider):
    def __init__(self, resourcename):
        self.filename = "/tmp/convertvideo_%s_%d.flv"%(os.path.basename(resourcename), random.randint(0,1000000))
        commands.getoutput("touch %s"%(commands.mkarg(self.getFileName())))
        fileflvstreamprovider.FileFlvStreamProvider.__init__(self,resourcename)
        cmd = ["sh", self.getShellConvertingScript(), resourcename, self.getFileName()]
        self.convertor=util.asynchronousprogramexecuter.AsynchronousProgramExecuter(cmd)
        
    def getShellConvertingScript(self):
        #this is an abstract class
        pass

    def getFileName(self):
        return self.filename

    def fileIsComplete(self):
        return self.convertor.hasfinished();
    
    def __del__(self):
        self.convertor.kill()
        os.unlink(self.getFileName())
        logging.info(self.convertor.getoutput())
        logging.info("stream deleted")

    @classmethod
    def supportsresource(cls, resourcename):
        '''returns whether a provider can provide the given resource'''
        #this is an abstract class
        return False
        
