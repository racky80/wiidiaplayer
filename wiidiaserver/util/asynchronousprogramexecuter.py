import thread, logging, os

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
        
    def kill(self):
        if self.hasfinished():
            logging.info("Not killing process, had already finished")
        else:
            logging.info("killing %d"%self.__p.pid)
            os.kill(self.__p.pid, 15)


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

    def getoutputsofar(self):
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


