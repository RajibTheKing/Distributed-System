from allimports import *

class OperationHistory:
    def __init__(self):
        self.operationLog = []
        self.lock = Lock()
    
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
    
    
