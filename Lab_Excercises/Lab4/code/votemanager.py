from allimports import *

class VoteManager:

    def __init__(self, serverList):
        self.numberOfServers = len(serverList)
        self.serverList = serverList
        self.algorithmState = 0
        self.initialize()
        
        

    def initialize(self):
        if self.algorithmState == 0:
            self.algorithmState = 1 #Algorithm State 1
            self.voteVector = []
            self.voteMatrix = []
            
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
        
        if self.voteFoundSoFar == self.numberOfServers:
            self.algorithmState = 2 #Algorithm State 2
        print(self.voteVector)
    
    def updateVoteMatrix(self, serverIP, data):
        print("updateVOteMatrix ===> ", serverIP)
        for i in range (0, self.numberOfServers):
            if self.serverList[i] == serverIP:
                self.voteMatrix[i] = data
                self.voteVectorSoFar += 1

        if self.voteVectorSoFar == self.numberOfServers:
            self.algorithmState = 4 #Algorithm State 4
        print(self.voteMatrix)
        

    def getVoteVector(self):
        return self.voteVector
    
    def getVoteMatrix(self):
        return self.voteMatrix
    
    def getAlgorithmState(self):
        return self.algorithmState
    
    def setAlgorithmState(self, value):
        self.algorithmState = value    #Algorithm State 3, set by Observer
    
    def isVoteAvailable(self, serverIP):
        for i in range(0, self.numberOfServers):
            if self.serverList[i] == serverIP:
                if self.voteVector[i] != "Unknown":
                    return True
                
        return False

    def getVotesFoundSofar(self):
        return self.voteFoundSoFar
    
    def getvoteVectorFoundSofar(self):
        return self.voteVectorSoFar

    def extractResult(self):
        print("NOW extract Result Can be processed")

    def getRandomVoteVector(self):
        randomVoteVector = []
        for i in range(0, self.numberOfServers):
            randomVoteVector.append(random.choice([u'Attack', u'Retreat']))
        return randomVoteVector

    


        
        





    