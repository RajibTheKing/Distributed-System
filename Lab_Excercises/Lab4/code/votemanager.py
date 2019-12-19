from allimports import *

class VoteManager:

    def __init__(self, serverList):
        self.results = []
        self.numberOfServers = len(serverList)
        self.initialize()
        self.serverList = serverList
        
        

    def initialize(self):
        self.results = []
        for i in range (0, self.numberOfServers):
            self.results.append("Unknown")
        self.resultsFoundSoFar = 0
    

    def updateVote(self, serverIP, vote):
        for i in range (0, self.numberOfServers):
            if self.serverList[i] == serverIP:
                self.results[i] = vote
                self.resultsFoundSoFar += 1

        print(self.results)

        
        





    