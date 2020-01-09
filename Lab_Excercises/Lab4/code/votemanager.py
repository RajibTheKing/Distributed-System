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
            self.voteVectorByzsent = []

            for i in range (0, self.numberOfServers):
                self.voteVector.append("Unknown")

            for i in range (0, self.numberOfServers):
                self.voteVectorByzsent.append("Unknown")    

            for i in range(0, self.numberOfServers):
                self.voteMatrix.append(self.voteVector)
            
            self.voteFoundSoFar = 0
            self.voteVectorSoFar = 0
            self.resultFoundSoFar = 'unknown'
    
    def start_nextRound(self):
        
        (vect, res) = self.calculateResult()
        self.voteVector = vect
        self.algorithmState = 3
        self.voteVectorSoFar = 0


    
    def setByzsent(self, serverIP, vote):
        for i in range (0, self.numberOfServers):
            if self.serverList[i] == serverIP:
                self.voteVectorByzsent[i] = vote
                


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

    def getRandomVoteVector(self,myip,toIP):
        randomVoteVector = []

        for i in range(0, self.numberOfServers):
            if toIP == self.serverList[i]:
                randomVoteVector.append(self.voteVector[i])
            elif myip == self.serverList[i]:
                randomVoteVector.append(self.voteVectorByzsent[self.serverList.index(toIP)])
            else:
                randomVoteVector.append(random.choice([u'Attack', u'Retreat']))
        return randomVoteVector

    def calculateResult(self):
        if self.getAlgorithmState() >= 4:
            numberOfServers = len(self.serverList)
            data = self.voteMatrix
            attacksCnt = [0] * numberOfServers
            retreatCnt = [0] * numberOfServers
            finalAttackCnt = 0
            finalRetreatCnt = 0
            resultVector = []
            for i in range(0, numberOfServers):
                for j in range(0, numberOfServers):
                    if i != j:
                        if data[i][j] == "Attack":
                            attacksCnt[j] = attacksCnt[j] + 1
                        else:
                            retreatCnt[j] = retreatCnt[j] + 1
                    
            for i in range(0, numberOfServers):
                if attacksCnt[i] > retreatCnt[i]:
                    resultVector.append("Attack")
                else:
                    resultVector.append("Retreat")
            
            for i in range(0, numberOfServers):
                if resultVector[i] == "Attack":
                    finalAttackCnt  = finalAttackCnt + 1
                else:
                    finalRetreatCnt = finalRetreatCnt + 1
            
            if finalAttackCnt > finalRetreatCnt:
                self.resultFoundSoFar = "Attack"
                return (resultVector, "Attack")
            else:
                self.resultFoundSoFar = "Retreat"
                return (resultVector, "Retreat")

        else:
            return ([], self.resultFoundSoFar) 

    


        
        





    