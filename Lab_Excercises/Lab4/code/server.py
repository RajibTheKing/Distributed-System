# coding=utf-8
# 7d03b7aaa0daa7a47b3748e174700be23730d09d

from allimports import *

# User defined modules
import mylogger
from byzantine_behavior import *
from votemanager import *


# ------------------------------------ ------------------------------------------------------------------
class Server(Bottle):

    def __init__(self, ID, IP, servers_list):
        super(Server, self).__init__()
        
        self.id = int(ID)
        self.ip = str(IP)
        self.servers_list = servers_list
        self.myLogger = mylogger.Logger(self.ip)
        self.myByzantine = Byzantine_Behavior()
        self.myVoteManager = VoteManager(self.servers_list)
        self.behavior = "Unknown"

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

        # list all REST URIs
        # if you add new URIs to the server, you need to add them here
        # API for Clients
        self.route('/', callback=self.index)
        self.post('/vote/attack', callback=self.post_vote_attack)
        self.post('/vote/retreat', callback=self.post_vote_retreat)
        self.post('/vote/byzantine', callback=self.post_vote_byzantine)
        
        # API for Scripts
        self.get('/serverlist', callback=self.get_serverlist)
        
        # API for Server Internals
        self.post('/propagate', callback=self.post_propagate)
        

        # we give access to the templates elements
        self.get('/lab4-html/<filename:path>', callback=self.get_template)
        # You can have variables in the URI, here's an example
        # self.post('/board/<element_id:int>/', callback=self.post_board) where post_board takes an argument (integer) called element_id
        thread = Thread(target=self.observer)
        thread.start()

    def observer(self):
        while True:
            if self.myVoteManager.getAlgorithmState() == 2:
                self.myVoteManager.setAlgorithmState(3)
                self.myVoteManager.updateVoteMatrix(self.ip, self.myVoteManager.getVoteVector())
                self.sendVoteVectors()
                
            elif self.myVoteManager.getAlgorithmState() == 4:
                self.myVoteManager.setAlgorithmState(5)
                print(self.myVoteManager.extractResult())
            else:
                pass

            time.sleep(2)

    

    def sendVoteVectors(self):
        if self.behavior == "Honest":
            payLoad = {
                "ip": self.ip,
                "type": "Vector",
                "data": self.myVoteManager.getVoteVector()
            }
            self.propagate_to_all_servers('/propagate', 'POST', dataToSend=json.dumps(payLoad))
        else: #"Byzantine"
            for srv_ip in self.servers_list:
                if srv_ip != self.ip: # don't propagate to yourself
                    payload = {
                        "ip": self.ip,
                        "type": "Vector",
                        "data": self.myVoteManager.getRandomVoteVector()
                    }
                    self.executor.submit(self.contact_another_server, srv_ip, '/propagate', 'POST', json.dumps(payload))
            


            


    def contact_another_server(self, srv_ip, URI, req='POST', dataToSend=None):
        # Try to contact another serverthrough a POST or GET
        # usage: server.contact_another_server("10.1.1.1", "/index", "POST", params_dict)
        success = False
        try:
            if 'POST' in req:
                #self.myLogger.addToQueue(self.ip + " => Sending to " + srv_ip+" , data = " + str(dataToSend))
                res = requests.post('http://{}{}'.format(srv_ip, URI), data=dataToSend )
            elif 'GET' in req:
                res = requests.get('http://{}{}'.format(srv_ip, URI))
            if res.status_code == 200:
                success = True
        except Exception as e:
            print("[ERROR] "+str(e))
        return success


    def propagate_to_all_servers(self, URI, req='POST', dataToSend=None):
        for srv_ip in self.servers_list:
            if srv_ip != self.ip: # don't propagate to yourself
                self.executor.submit(self.contact_another_server, srv_ip, URI, req, dataToSend)


    def index(self):
        self.myLogger.addToQueue("Inside index")
        (vect, res) = self.calculateResult()
        return template('lab4-html/index.html', dataVector=self.myVoteManager.getVoteMatrix(), resultVector=vect, finalResult=res)
       
    
    def calculateResult(self):
        if self.myVoteManager.getAlgorithmState() >= 4:
            numberOfServers = len(self.servers_list)
            data = self.myVoteManager.getVoteMatrix()
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
                return (resultVector, "Attack")
            else:
                return (resultVector, "Retreat")

        else:
            return ([], "Unknown")                                                  

    # get on ('/serverlist')
    def get_serverlist(self):
        return json.dumps(self.servers_list)
    
    # get all message 
    def get_board_data(self):
        return json.dumps(self.blackboard.get_content())




    def get_template(self, filename):
        return static_file(filename, root='./lab4-html/')
    
    def remove_server(self, ipToRemove):
        if ipToRemove in self.servers_list:
            self.servers_list.remove(ipToRemove)


    

    def post_vote_attack(self):
        if self.myVoteManager.isVoteAvailable(self.ip) == False:
            self.behavior = "Honest"
            self.myLogger.addToQueue("inside post_vote_attack")
            self.myVoteManager.initialize()
            self.myVoteManager.updateVote(self.ip, u'Attack')
            payload = {
                "ip": self.ip,
                "type": "Single",
                "vote": "Attack"
            }
            self.propagate_to_all_servers('/propagate', 'POST', dataToSend=json.dumps(payload))
            return 'Voted ATTACK'
        else:
            return 'Message: Algorithm is already initialized with server type ' + self.behavior
    
    def post_vote_retreat(self):
        if self.myVoteManager.isVoteAvailable(self.ip) == False:
            self.behavior = "Honest"
            self.myLogger.addToQueue("inside post_vote_retreat")
            self.myVoteManager.initialize()
            self.myVoteManager.updateVote(self.ip, u'Retreat')
            payload = {
                "ip": self.ip,
                "type": "Single",
                "vote": "Retreat"
            }
            self.propagate_to_all_servers('/propagate', 'POST', dataToSend=json.dumps(payload))
            return "Voted RETREAT"
        else:
            return "Message: Algorithm is already initialized with server type " + self.behavior


    def post_vote_byzantine(self):
        if self.myVoteManager.isVoteAvailable(self.ip) == False:
            self.behavior = "Byzantine"
            self.myLogger.addToQueue("inside post_vote_byzantine")
            self.myVoteManager.initialize()
            self.myVoteManager.updateVote(self.ip, random.choice([u'Attack', u'Retreat']))
            

            for srv_ip in self.servers_list:
                if srv_ip != self.ip: # don't propagate to yourself
                    payload = {
                        "ip": self.ip,
                        "type": "Single",
                        "vote": random.choice([u'Attack', u'Retreat'])
                    }
                    self.executor.submit(self.contact_another_server, srv_ip, '/propagate', 'POST', json.dumps(payload))
            
            return "Became Byzantine"
        else:
            return "Message: Algorithm is already initialized with server type " + self.behavior

    # post on ('/propagate')
    def post_propagate(self):
        data = list(request.body)
        parsedItem = json.loads(data[0])
        if parsedItem["type"] == "Single":
            self.myVoteManager.updateVote(parsedItem['ip'], parsedItem['vote'])
        elif parsedItem["type"] == "Vector":
            self.myVoteManager.updateVoteMatrix(parsedItem['ip'], parsedItem['data'])
        else:
            print("Invalid Message type")
        
                    


        



        

# ------------------------------------------------------------------------------------------------------
def main():
    PORT = 80
    parser = argparse.ArgumentParser(description='Your own implementation of the distributed blackboard')
    parser.add_argument('--id',
                        nargs='?',
                        dest='id',
                        default=1,
                        type=int,
                        help='This server ID')
    parser.add_argument('--servers',
                        nargs='?',
                        dest='srv_list',
                        default="10.1.0.1,10.1.0.2",
                        help='List of all servers present in the network')
    args = parser.parse_args()
    server_id = args.id
    server_ip = "10.1.0.{}".format(server_id)
    servers_list = args.srv_list.split(",")

    try:
        server = Server(server_id,
                        server_ip,
                        servers_list)
        bottle.run(server,
                   host=server_ip,
                   port=PORT)
    except Exception as e:
        print("[ERROR] "+str(e))


# ------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    main()
