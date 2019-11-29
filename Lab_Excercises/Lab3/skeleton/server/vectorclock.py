from allimports import *

class VectorClock:

    def __init__(self, index, nserver):
        self.serverIndex = index
        self.numberOfServers = nserver
        self.currentClockTime = 0
        self.vclock = []
        for x in range(0, self.numberOfServers):
            self.vclock.append(0)
        self.lock = Lock()

    def getNext(self):
        with self.lock:
            self.currentClockTime = self.currentClockTime+1
            self.vclock[self.serverIndex] = self.currentClockTime
            return self.vclock
    
    def updateClock(self, updatedClock):
        with self.lock:
            for x in range(0, self.numberOfServers):
                if x == self.serverIndex:
                    newTime = max(self.currentClockTime, updatedClock[x])
                    self.currentClockTime = newTime + 1
                    self.vclock[x] = self.currentClockTime
                else:
                    self.vclock[x] = max(updatedClock[x], self.vclock[x])
                


        
