
from allimports import *
from operation_history import OperationHistory


class Blackboard():

    def __init__(self, vclock, logger):
        currentTimeStamp = time.time()
        self.content = []
        # self.content[1] = {"entry": "First", "createdAt": currentTimeStamp}
        self.lock = Lock() # use lock when you modify the content
        self.vectorClock = vclock
        self.operationLog = OperationHistory()
        self.myLogger = logger
        self.queue = Queue.Queue(100)
        thread = Thread(target=self.consume)
        thread.start()


    def get_content(self): #O(1)
        with self.lock:
            cnt = self.content
            return cnt

    def propagateContent(self, operationType, parsedItem):
        with self.lock:
            self.queue.put((operationType, parsedItem))

    def add_content(self, new_content): #O(1)
        with self.lock:
            currentTimeStamp = time.time()
            nowID = str(uuid.uuid1())
            nowClock = self.vectorClock.getNext()
            newValue  =  {"id": nowID, "entry": new_content, "createdAt": currentTimeStamp, "vclock": nowClock}
            self.content.append(newValue)

            #also add to the history log
            log = {"Operation" : "add", "element": newValue, "index": len(self.content) - 1}
            self.operationLog.addHistory(log)
            
            return newValue

    def set_content(self,number, modified_entry): 
        with self.lock:
            #Need to Improve 
            for i in range(0, len(self.content)):
                if self.content[i]['id'] == number:
                    oldElement = copy.deepcopy(self.content[i])
                    nowClock = self.vectorClock.getNext()
                    self.content[i]['entry'] = modified_entry
                    self.content[i]['vclock'] = nowClock

                    #also add to the history log
                    log = {"Operation" : "modify", "element-old": oldElement, "element": copy.deepcopy(self.content[i])}
                    self.operationLog.addHistory(log)


                    return self.content[i]
            
    
    def delete_content(self, number):
        with self.lock:
            for i in range(0, len(self.content)):
                if self.content[i]['id'] == number:
                    nowClock = self.vectorClock.getNext()
                    self.content[i]['vclock'] = nowClock
                    ret = self.content[i]
                    del self.content[i]

                    #also add to the history log
                    log = {"Operation" : "delete", "element": ret, "index": i}
                    self.operationLog.addHistory(log)

                    return ret

    def rollback(self, log):
        if log["Operation"] == "add":
            self.myLogger.addToQueue("Inside ROLLBAAACK!!!! " + str(log))
            del self.content[log["index"]]
        else:
            pass
        

    def commit(self, log):
        if log["Operation"] == "add":
            self.myLogger.addToQueue("Inside COMMIT##### " + str(log))
            self.content.append(log["element"])

            #also add to the history log
            log = {"Operation" : "add", "element": log["element"], "index": len(self.content) - 1}
            self.operationLog.addHistory(log)
        else:
            pass

    def isShifted(self, newElement, log):
        if log == None:
            return False

        (elementClock, elementIndex) = newElement["vclock"]
        (logClock, logIndex) = log["element"]["vclock"]
        if elementClock[elementIndex] > logClock[logIndex]:
            return False
        elif elementClock[elementIndex] == logClock[logIndex]:
            if elementIndex > logIndex:
                return False
            else:
                return True
        else:
            return True

    def consume(self):
        while True:
            while not self.queue.empty():
                (operationType, parsedItem) = self.queue.get()
                self.vectorClock.updateClock(parsedItem["vclock"][0])
                if operationType == "add":
                    myStack = []
                    while self.isShifted(parsedItem, self.operationLog.getLast()):
                        lastLog = self.operationLog.getLast()
                        if lastLog != None:
                            myStack.append(self.operationLog.getLast())
                            self.rollback(self.operationLog.getLast())
                            self.operationLog.deleteLast()

                    self.content.append(parsedItem)
                    #also add to the history log
                    log = {"Operation" : "add", "element": parsedItem, "index": len(self.content) - 1}
                    self.operationLog.addHistory(log)

                    while len(myStack) != 0:
                        self.commit(myStack.pop())

                elif operationType == "modify":
                    for i in range(0, len(self.content)):
                        if self.content[i]['id'] == parsedItem['id']:
                            self.content[i] = parsedItem
                elif operationType == "delete":
                    for i in range(0, len(self.content)):
                        if self.content[i]['id'] == parsedItem['id']:
                            del self.content[i]
                            
                else:
                    pirnt("Invalid Propagation")
                time.sleep(0.5)
            time.sleep(1)

