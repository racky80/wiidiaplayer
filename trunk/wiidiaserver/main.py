#!/usr/bin/python 

from twisted.web import server, resource, static
from twisted.internet import reactor, protocol, error
import os, urllib, sys, logging, getopt, errno, time
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

def printHelp():
    # Some help information
    print "Usage: main.py -m <mediadir> [-dvh] [-r <rootdir>]"
    print
    print "Options:"
    print "  -d   fork daemon process"
    print "  -v   print version information"
    print "  -r   root directory"
    print "  -m   media directory"
    print "  -h   print this message"

def printVersion():
    # Here you are... Do with it whatever you want
    print "Wiidiaplayer v0.0.0.5"
    print
    print "Your copyrights here ;)"


def readPidFile(pidPath):
    # Read the pid file, return none if not exist
    if os.path.exists(pidPath):
        try:
            pidFile = open(pidPath)
            pid = pidFile.read()
            pidFile.close()
            return int(pid.strip())
        except (ValueError, IOError):
            return None
    else:
        return None

def savePidFile(pidPath):
    # Save pid to file:
    try:
        pid = os.getpid()
        pidFile = open(pidPath, 'w')
        pidFile.write(str(pid))
        pidFile.close()
    except OSError:
        print "Can't save the pid to %s" % pidPath
        sys.exit(1)

def deletePidFile(pidPath):
    # Now unlink the pid file
    try:
        os.unlink(pidPath)
    except OSError:
        print "Can't unlink the pidPath file %s" % pidPath
        sys.exit(1)


def livePid(pid):
    # Is this pid still up?
    try:
        os.kill(pid, 0)
        return pid
    except OSError, e:
        if e.errno == errno.EPERM:
            return pid
    return None

def killPid(pid):
    # Try to kill the old pid file
    if pid:
        for j in range(10):
            if not livePid(pid):
                break
            os.kill(pid, 15)
            time.sleep(1)
        else:
            print "Can't kill process %s" % pid


def daemonize():
    # Do a first fork
    try:
        pid = os.fork() 
        if pid > 0:
            sys.exit(0) 
    except OSError:
        print "Can't fork this process (first fork)"
        sys.exit(1)
    
    # Might consider changing this part:    
    os.chdir(os.path.abspath(sys.path[0]))
    os.setsid()
    os.umask(0)
    
    # Do a second fork fork
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0) 
    except OSError:
        print "Can't fork this process (second fork)"
        sys.exit(1)
    
    # Write keyboard input to nothing
    dev_null = file('/dev/null', 'r')
    os.dup2(dev_null.fileno(), sys.stdin.fileno())
    dev_null.close()

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hdvr:m:")
    except getopt.GetoptError:
        printHelp()
        sys.exit(2)
    
    fork = False
    rootdir = "root"
    mediadir = ""
    
    # Check what command we should call
    for o, a in opts:
        if o == '-d':
            fork = True
        if o == '-h':
            printHelp()
            sys.exit()
        if o == '-v':
            printVersion()
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
    #    printHelp()
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
    
    # Save pid file (needs to be adjusted to a neat set of functions):
    pidPath = '/var/run/wiidiaplayer.pid'
    
    if os.path.exists(pidPath):
        # Check if old thread is running, kill it if so:
        oldPid = readPidFile(pidPath)
        if oldPid:
            # Kill this pid
            killPid(oldPid)
            # Also delete the pidFile
            deletePidFile(pidPath)
        # Now save the pidFile
        savePidFile(pidPath)
    
    # Here is your normal code...
    logging.basicConfig(level=logging.INFO)
    logging.info("Using %s as rootdir" %rootdir)
    
    root = static.File(rootdir)
    root.putChild('getdir',GetDir())
    root.putChild('feedback',PrintFeedback())
    site = server.Site(root)
    reactor.listenTCP(1935, rtmp.RTMPServerFactory( ))
    reactor.listenTCP(8080, site)
    reactor.run()



if __name__ == '__main__':
    main()