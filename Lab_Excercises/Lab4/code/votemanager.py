from allimports import *

class VoteManager:

    def __init__(self, serverList):
        self.numberOfServers = len(serverList)
        self.serverList = serverList
        self.initialize()
        
        

    def initialize(self):
        self.voteVector = []
        self.voteMatrix = []
        self.algorithmState = 1 #Algorithm Step 1

        
        for i in range (0, self.numberOfServers):
            self.voteVector.append("Unknown")
        for i in range(0, self.numberOfServers):
            self.voteMatrix.append(self.voteVector)
        
        self.voteFoundSoFar = 0
        self.voteVectorSoFar = 0
    

    def updateVote(self, serverIP, vote):
        for i in range (0, self.numberOfServers):
            if self.serverList[i] == serverIP:
                self.voteVector[i] = vote
                self.voteFoundSoFar += 1

        print(self.voteVector)

    def getVotes(self):
        return self.voteVector
    
    def getAlgorithmState(self):
        return self.algorithmState
    
    def isVoteAvailable(self, serverIP):
        for i in range(0, self.numberOfServers):
            if self.serverList[i] == serverIP:
                if self.voteVector[i] != "Unknown":
                    return True
                
        return False


    


        
        





    