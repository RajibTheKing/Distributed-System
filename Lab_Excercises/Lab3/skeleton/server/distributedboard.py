
from allimports import *


class Blackboard():

    def __init__(self):
        currentTimeStamp = time.time()
        self.content = dict()
        # self.content[1] = {"entry": "First", "createdAt": currentTimeStamp}
        self.lastWrittenID = 0
        self.lock = Lock() # use lock when you modify the content



    def get_content(self): #O(1)
        with self.lock:
            cnt = self.content
            return cnt

    def propagateContent(self, parsedItem): #O(1) Expected
        with self.lock:
            self.content[parsedItem['id']] = {"entry": parsedItem['entry'], "createdAt": parsedItem['createdAt']}
            self.lastWrittenID = parsedItem['id']

    def add_content(self, new_content): #O(1) Expected
        with self.lock:
            currentTimeStamp = time.time()
            nowID = self.lastWrittenID + 1
            newValue  =  {"id": nowID, "entry": new_content, "createdAt": currentTimeStamp}
            self.content[nowID] = {"entry": new_content, "createdAt": currentTimeStamp}
            self.lastWrittenID = nowID
            return newValue

    def set_content(self,number, modified_entry): # O(1) Expected
        with self.lock:
            prevValue = self.content[number]
            self.content[number] = {"entry" : modified_entry, "createdAt": prevValue["createdAt"]}
    
    def delete_content(self, number): # O(1) Expected
        with self.lock:
            if self.content.has_key(number):
                self.content.pop(number)
            else:
                print("Error in delete_content key not found " + str(number))