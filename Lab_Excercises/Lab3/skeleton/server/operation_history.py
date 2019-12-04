from allimports import *

class OperationHistory:
    def __init__(self, logger):
        self.operationLog = []
        self.lock = RLock()
        self.myLogger = logger
    
    def addHistory(self, content):
        with self.lock:
            self.operationLog.append(content)
    
    def getLast(self):
        with self.lock:
            if len(self.operationLog) == 0:
                return None
            return copy.deepcopy(self.operationLog[-1])

    def deleteLast(self):
        with self.lock:
            del self.operationLog[-1]

    def getHistory(self):
        with self.lock:
            self.operationLog

    def getSize(self):
        with self.lock:
            return len(self.operationLog)

    def getAllOperationTime(self):
        with self.lock:
            vclockList = []
            for x in self.operationLog:
                vclockList.append(x["element"]["vclock"])
            return vclockList
    
    def getComplementedLog(self, vClockList):
        with self.lock:
            ret = []
            for x in self.operationLog:
                clk = x["element"]["vclock"]
                if clk not in vClockList:
                    self.myLogger.addToQueue(str(clk) + " --> " + str(vClockList))
                    ret.append(x)
            
            return ret







    
    
