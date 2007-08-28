from twisted.web import server, resource, static
from twisted.internet import reactor, protocol, error
import os, urllib, sys, logging
import rtmp

sys.path.append(os.path.dirname(__file__));


class ProcessPassthroughprotocol(protocol.ProcessProtocol):

    def __init__(self, request):
        self.request=request
        pass

    def connectionMade(self): pass

    def outReceived(self, data):
        if self.request.connectionclosed:
            self.transport.closeStdout()
            print "killed"
        self.request.write(data)
        
    def errReceived(self,data):
        print ("stderr: %s"%data)
        
    def outConnectionLost(self): pass
    def errConnectionLost(self): pass
    def inConnectionLost(self): pass
    
    def processEnded(self, reason):
        self.request.finish();
        print "Process ended: %s"%reason

class ProcessPassthroughprotocolUrlEncoded(ProcessPassthroughprotocol):
    firstdata=True
    def outReceived(self, data):
        if self.firstdata:
	    self.firstdata=False
	    dataprefix="result="
	else:
	    dataprefix=""
        ProcessPassthroughprotocol.outReceived(self,dataprefix+urllib.quote(data))

class WiiServerExternalprogramResource(resource.Resource):
    isLeaf=True
    DEFAULTPATH="/mnt/media/"

    def render_GET(self, request):
        self.request=request
        self.request.connectionclosed=False
        path = os.path.abspath('/'+os.path.sep.join(request.postpath));
        fullpath=os.path.abspath(self.DEFAULTPATH+path);
        processProtocolClass=self.getProcessPassthroughClass()
        processProtocol=processProtocolClass(request);
        ext=os.path.splitext(fullpath)[1]
        executable, arg = self.getCommand(fullpath)
        reactor.spawnProcess(processProtocol, executable, arg)
        request.connectionLost=self.connectionClosed
        return server.NOT_DONE_YET

    def connectionClosed(self, reason):
        self.request.connectionclosed=True
        print "Help, I'm closed"

class PrintFeedback(resource.Resource):
    isLeaf=True
    def render_GET(self, request):
        print ("Feedback recieved: %s"%'/'.join(request.postpath))
        return ("Feedback recieved: %s"%request.postpath)


class GetDir(WiiServerExternalprogramResource):
    def getCommand(self, fullpath):
        executable='/bin/ls'
        return executable, [executable, '-1l', fullpath]

    def getProcessPassthroughClass(self):
        return ProcessPassthroughprotocolUrlEncoded

class GetInfo(WiiServerExternalprogramResource):
    def getCommand(self, fullpath):
        executable='/usr/bin/midentify'
        return executable, [executable, fullpath]

    def getProcessPassthroughClass(self):
        return ProcessPassthroughprotocolUrlEncoded

class GetFile(WiiServerExternalprogramResource):
    def getCommand(self, fullpath):
        ext=os.path.splitext(fullpath)[1]
        if ext == "mp3" or ext=="ogg":
            return self.getAudioRenderCommand(fullpath)
        else:
            return self.getVideoRenderCommand(fullpath)

    def getAudioRenderCommand(self, sourcefilename):
        return '/usr/bin/ffmpeg', ['/usr/bin/ffmpeg', '-i', sourcefilename, '-f', 'flv', '-acodec', 'mp3', '-ab', '192', '-ar', '44100', '-ac', '2', '-']

    def getVideoRenderCommand(self, sourcefilename):
        return 'convertvideo.sh', ['convertvideo.sh', sourcefilename]

    def getProcessPassthroughClass(self):
        return ProcessPassthroughprotocol
    
logging.basicConfig(level=logging.INFO)
try:
    rootdir = sys.argv[1]
except IndexError:
    rootdir = "root"

logging.info("Using %s as rootdir" %rootdir);


root = static.File(rootdir)
root.putChild('getdir',GetDir())
root.putChild('getfile',GetFile())
root.putChild('getinfo',GetInfo())
root.putChild('feedback',PrintFeedback())
site = server.Site(root)
reactor.listenTCP(1935, rtmp.RTMPServerFactory( ))
reactor.listenTCP(80, site)
reactor.run()
