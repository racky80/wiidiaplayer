#!/usr/bin/python 

from twisted.web import server, resource, static
from twisted.internet import reactor, protocol, error
import os, urllib, sys, logging, getopt
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
    
def print_help():
    # Some help information
    print "Usage: main.py -m <mediadir> [-dvh] [-r <rootdir>]"
    print
    print "Options:"
    print "  -d   fork daemon process"
    print "  -v   print version information"
    print "  -r   root directory"
    print "  -m   media directory"
    print "  -h   print this message"

def print_version():
    # Here you are... Do with it whatever you want
    print "Wiidiaplayer v0.0.0.5"
    print
    print "Your copyrights here ;)"


def daemonize():
    try:
        pid = os.fork() 
        if pid > 0:
            sys.exit(0) 
    except OSError:
        print "fork() failed"
        sys.exit(1)
    
    # Might consider changing this part:    
    os.chdir(os.path.dirname(__file__))
    os.setsid()
    os.umask(0)
    
    # Try to get the pid, if it fails exit
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0) 
    except OSError:
        print "fork() failed"
        sys.exit(1)
    
    # You might want to save the pid to /var/run/<name>.pid, you can deside wheter or not do that
    #pidFile = 
    
    # Write keyboard input to nothing
    dev_null = file('/dev/null', 'r')
    os.dup2(dev_null.fileno(), sys.stdin.fileno())
    dev_null.close()

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hdvr:m:")
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    
    fork = False
    rootdir = "root"
    mediadir = ""
    
    # Check what command we should call
    for o, a in opts:
        if o == '-d':
            fork = True
        if o == '-h':
            print_help()
            sys.exit()
        if o == '-v':
            print_version()
            sys.exit()
        if o == '-r':
            rootdir = a
        if o == '-m':
            mediadir = a
    
    # Currently checking what's the best way to pass mediadir through to rtmp
    #if mediadir:
        # Send it to the scripts who needs this dir
    #    mediadir = mediadir
    #else:
    #    print_help()
    #    sys.exit(0)
    
    # We are going to daemonize, first only save the logs:
    if fork:
        try:
            sys.stderr.fileno
            sys.stdout.fileno
            # Now we save it to /var/log/wiidiaplayer
            out_log = file('/var/log/wiidiaplayer', 'a+', 0)
            sys.stderr.flush()
            sys.stdout.flush()
            os.dup2(out_log.fileno(), sys.stderr.fileno())
            os.dup2(out_log.fileno(), sys.stdout.fileno())
            out_log.close()
            # Now daemonize it all:
            daemonize()
        except AttributeError:
            pass
    
    # Here is your normal code...
    logging.basicConfig(level=logging.INFO)
    logging.info("Using %s as rootdir" %rootdir)
    
    root = static.File(rootdir)
    root.putChild('getdir',GetDir())
    root.putChild('getfile',GetFile())
    root.putChild('getinfo',GetInfo())
    root.putChild('feedback',PrintFeedback())
    site = server.Site(root)
    reactor.listenTCP(1935, rtmp.RTMPServerFactory( ))
    reactor.listenTCP(8080, site)
    reactor.run()

if __name__ == '__main__':
    main()