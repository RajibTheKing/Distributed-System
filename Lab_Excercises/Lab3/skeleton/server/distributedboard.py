
from allimports import *


class Blackboard():

    def __init__(self):
        currentTimeStamp = time.time()
        self.content = []
        # self.content[1] = {"entry": "First", "createdAt": currentTimeStamp}
        self.lastWrittenID = 0
        self.lock = Lock() # use lock when you modify the content



    def get_content(self): #O(1)
        with self.lock:
            cnt = self.content
            return cnt

    def propagateContent(self, parsedItem): #O(1) Expected
        with self.lock:
            dataToAdd = {
                            "id": parsedItem['id'], 
                            "entry": parsedItem['entry'], 
                            "createdAt": parsedItem['createdAt']
                        }
            self.content.append(dataToAdd)
            self.lastWrittenID = parsedItem['id']

    def add_content(self, new_content): #O(1) Expected
        with self.lock:
            currentTimeStamp = time.time()
            nowID = self.lastWrittenID + 1
            newValue  =  {"id": nowID, "entry": new_content, "createdAt": currentTimeStamp}
            self.content.append(newValue)
            self.lastWrittenID = nowID
            return newValue

    def set_content(self,number, modified_entry): # O(1) Expected
        with self.lock:
            #Need to Improve 
            for i in range(0, len(self.content)):
                if self.content[i]['id'] == number:
                    self.content[i]['entry'] = modified_entry
                    break
            
    
    def delete_content(self, number): # O(1) Expected
        with self.lock:
            for i in range(0, len(self.content)):
                if self.content[i]['id'] == number:
                    del self.content[i]
                    break