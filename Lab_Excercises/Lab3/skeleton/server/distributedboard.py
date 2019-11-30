
from allimports import *


class Blackboard():

    def __init__(self, vclock):
        currentTimeStamp = time.time()
        self.content = []
        # self.content[1] = {"entry": "First", "createdAt": currentTimeStamp}
        self.lock = Lock() # use lock when you modify the content
        self.vectorClock = vclock

    def get_content(self): #O(1)
        with self.lock:
            cnt = self.content
            return cnt

    def propagateContent(self, operationType, parsedItem): #O(1) Expected
        with self.lock:
            self.vectorClock.updateClock(parsedItem["vclock"][0])
            if operationType == "add":
                self.content.append(parsedItem)
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

    def add_content(self, new_content): #O(1) Expected
        with self.lock:
            currentTimeStamp = time.time()
            nowID = str(uuid.uuid1())
            nowClock = self.vectorClock.getNext()
            newValue  =  {"id": nowID, "entry": new_content, "createdAt": currentTimeStamp, "vclock": nowClock}
            self.content.append(newValue)
            return newValue

    def set_content(self,number, modified_entry): # O(1) Expected
        with self.lock:
            #Need to Improve 
            for i in range(0, len(self.content)):
                if self.content[i]['id'] == number:
                    nowClock = self.vectorClock.getNext()
                    self.content[i]['entry'] = modified_entry
                    self.content[i]['vclock'] = nowClock
                    return self.content[i]
            
    
    def delete_content(self, number): # O(1) Expected
        with self.lock:
            for i in range(0, len(self.content)):
                if self.content[i]['id'] == number:
                    nowClock = self.vectorClock.getNext()
                    self.content[i]['vclock'] = nowClock
                    ret = self.content[i]
                    del self.content[i]
                    return ret