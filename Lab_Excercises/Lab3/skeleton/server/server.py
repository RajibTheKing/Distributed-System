# coding=utf-8
from allimports import *

# User defined modules
import distributedboard
import mylogger
from serverState import State
from myMsgType import MsgType


# ------------------------------------ ------------------------------------------------------------------
class Server(Bottle):

    def __init__(self, ID, IP, servers_list):
        super(Server, self).__init__()
        self.blackboard = distributedboard.Blackboard()
        self.id = int(ID)
        self.ip = str(IP)
        self.servers_list = servers_list
        self.leader_server = "Not Selected Yet"
        # print(servers_list)
        self.myLogger = mylogger.Logger(self.ip)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

        # list all REST URIs
        # if you add new URIs to the server, you need to add them here
        self.hook('before_request')(self.check_srv_mode)
        self.get('/busy',callback=self.get_busy,no_hook = True)
        

        # API for Clients
        self.route('/', callback=self.index, no_hook=True)
        self.get('/board', callback=self.get_board, no_hook=True)
        self.post('/', callback=self.post_index)
        self.post('/board', callback=self.post_board)
        self.post('/board/<number:int>/', callback=self.post_board_ID)
        
        # API for Scripts
        self.get('/serverlist', callback=self.get_serverlist, no_hook=True)
        self.get('/board/alldata',callback=self.get_board_data , no_hook=True)
        
        # API for Server Internals
        self.post('/propagate', callback=self.post_propagate, no_hook=True)
        self.post('/propagate_deletemodify', callback=self.post_propagate_deletemodify, no_hook=True)
        self.post('/server_controller', callback=self.post_ServerController, no_hook=True)


        # we give access to the templates elements
        self.get('/templates/<filename:path>', callback=self.get_template)
        # You can have variables in the URI, here's an example
        # self.post('/board/<element_id:int>/', callback=self.post_board) where post_board takes an argument (integer) called element_id
        
        self.electionProcess = False
        self.firstRun = True
        self.serverState = State.ELECTION_MODE

        self.executor.submit(self.KeepAliveCheck)
        if self.ip == min(self.servers_list):
            self.executor.submit(self.start_election)
        self.lastSentMessage = None

        

    def do_parallel_task(self, method, args=None):
        # create a thread running a new task
        # Usage example: self.do_parallel_task(self.contact_another_server, args=("10.1.0.2", "/index", "POST", params_dict))
        # this would start a thread sending a post request to server 10.1.0.2 with URI /index and with params params_dict
        thread = Thread(target=method,
                        args=args)
        thread.daemon = True
        thread.start()


    def do_parallel_task_after_delay(self, delay, method, args=None):
        # create a thread, and run a task after a specified delay
        # Usage example: self.do_parallel_task_after_delay(10, self.start_election, args=(,))
        # this would start a thread starting an election after 10 seconds
        thread = Thread(target=self._wrapper_delay_and_execute,
                        args=(delay, method, args))
        thread.daemon = True
        thread.start()


    def _wrapper_delay_and_execute(self, delay, method, args):
        time.sleep(delay) # in sec
        method(*args)


    def contact_another_server(self, srv_ip, URI, req='POST', dataToSend=None):
        # Try to contact another serverthrough a POST or GET
        # usage: server.contact_another_server("10.1.1.1", "/index", "POST", params_dict)
        success = False
        try:
            if 'POST' in req:
                self.myLogger.addToQueue(self.ip + " => Sending to " + srv_ip+" , data = " + str(dataToSend))
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
                # self.do_parallel_task(self.contact_another_server, args=(srv_ip, URI, req, dataToSend))
                self.executor.submit(self.contact_another_server, srv_ip, URI, req, dataToSend)
                #success =  self.contact_another_server(srv_ip, URI, req, dataToSend)
                #if not success:
                #    print("[WARNING ]Could not contact server {}".format(srv_ip))


    # route to ('/')
    def index(self):
        # we must transform the blackboard as a dict for compatiobility reasons
        boardData = self.blackboard.get_content()
        board = dict()
        for i in boardData:
            x = boardData[i]
            board[i] = x["entry"]
        
        return template('server/templates/index.tpl',
                        board_title='Server {} ({})'.format(self.id,
                                                            self.ip),
                        board_dict=board.iteritems(),
                        members_name_string='INPUT YOUR NAME HERE')
       

    # get on ('/board')
    def get_board(self):
        # we must transform the blackboard as a dict for compatibility reasons
        boardData = self.blackboard.get_content()
        board = dict()
        for i in boardData:
            x = boardData[i]
            board[i] = x["entry"]
        return template('server/templates/blackboard.tpl',
                        board_title='Server {} ({})'.format(self.id,
                                                            self.ip),
                        board_dict=board.iteritems())
    # get on ('/serverlist')
    def get_serverlist(self):
        return json.dumps(self.servers_list)
    
    # get all message 
    def get_board_data(self):
        return self.blackboard.get_content()


    # post on ('/board') add new entry
    def post_board(self):
        print("inside postboard")
        newEntry = request.forms.get('entry')
        self.myLogger.addToQueue('post_board: ' + newEntry)
        
        if self.ip == self.leader_server:
            addedItem = self.blackboard.add_content(newEntry)
            self.propagate_to_all_servers(URI="/propagate", req="POST", dataToSend=json.dumps(addedItem))
        else:
            payload = {
                'entry': newEntry,
            }
            self.contact_another_server(self.leader_server, URI='/board', req="POST", dataToSend=payload)
            redirect('/')
        
        

    # post on ('/board/<number>)
    def post_board_ID(self, number):
        option = request.forms.get('delete')
        modified_entry = request.forms.get('entry')

        if option == "1":
            self.myLogger.addToQueue('DELETE : ' + str(number))
        else:
            self.myLogger.addToQueue('MODIFY : ' + str(number) + " => " + modified_entry)

        
        if self.leader_server == self.ip:
            if option == "1":
                self.blackboard.delete_content(number)
                self.propagate_to_all_servers(URI="/propagate_deletemodify", req="POST", dataToSend=json.dumps(
                    {
                        "value": option, 
                        "number": number
                    }))
                
            else:
                self.blackboard.set_content(number,modified_entry)
                self.propagate_to_all_servers(URI="/propagate_deletemodify", req="POST", dataToSend=json.dumps(
                    {
                        "value": option, 
                        "number": number,
                        "entry": modified_entry
                    }))
        else:
            payload = {
                'delete': option,
                'entry': modified_entry,
            }
            self.contact_another_server(self.leader_server, URI='/board/{0}/'.format(number), req="POST", dataToSend=payload)


        redirect('/')


    # post on ('/propagate')
    def post_propagate(self):
        data = list(request.body)
        parsedItem = json.loads(data[0])
        self.blackboard.propagateContent(parsedItem)
    
    # post on ('/propagate_deletemodify/)
    def post_propagate_deletemodify(self):
        data = list(request.body)
        parsed = json.loads(data[0])
        option = parsed['value']
        if option == "1":
            number = parsed['number']
            self.blackboard.delete_content(number)
        else:
            number = parsed['number']
            modified_entry = parsed['entry']
            self.blackboard.set_content(number,modified_entry)


    # GET /BUSY
    def get_busy(self):
        return "server is busy"
        

    # post on ('/')
    def post_index(self):
        try:
            # we read the POST form, and check for an element called 'entry'
            new_entry = request.forms.get('entry')
        except Exception as e:
            print("[ERROR] "+str(e))


    def get_template(self, filename):
        return static_file(filename, root='./server/templates/')


    def start_election(self):
        self.serverState = State.ELECTION_MODE
        if self.firstRun:
            time.sleep(5)
        self.firstRun = False
        self.electionProcess = True

        for x in self.servers_list:
            if x != self.ip:
                toSend = {
                    "message_type": MsgType.INITIATE_ELECTION
                }
                self.executor.submit(self.contact_another_server, x, URI="/server_controller", req="POST", dataToSend=json.dumps(toSend))
            
        self.serverState = State.ELECTION_MODE

        #Bully Algorithm Starts
        for x in self.servers_list:
            if x > self.ip:
                toSend = {
                    "message_type": MsgType.BULLY_ELECTION,
                    "ip": self.ip
                }
                self.executor.submit(self.contact_another_server, x, URI="/server_controller", req="POST", dataToSend=json.dumps(toSend))

        


        # Wait until election completes
        while(self.electionProcess ):
            time.sleep(1)
        
        self.serverState = State.SERVING_MODE
    

    @hook('before_request')
    def check_srv_mode(self):
        print("inside check srv mode "+str(self.serverState))

        currentPath = str(request['bottle.request'])
        if "GET" in currentPath:
            if self.serverState != State.SERVING_MODE:
                redirect("/busy")
        elif "POST" in currentPath:
            if "/board" in currentPath:
                if self.serverState != State.SERVING_MODE:
                    redirect("/busy")
        else:
            pass
    
    def post_ServerController(self):
        data = list(request.body)
        parsedItem = json.loads(data[0])
        self.myLogger.addToQueue(str(parsedItem) + " serverMode = " + str(self.serverState))
        if parsedItem['message_type'] == MsgType.REMOVE_SERVER:
            self.remove_server(parsedItem["ip"])
            return "Server Removed " + parsedItem["ip"]
        elif parsedItem['message_type'] == MsgType.CHECK_ALIVE:
            return MsgType.PRESENT
        elif parsedItem['message_type'] == MsgType.INITIATE_ELECTION:
            if self.serverState == State.SERVING_MODE:
                self.serverState = State.ELECTION_MODE

        elif parsedItem['message_type'] == MsgType.BULLY_ELECTION:
            if self.serverState == State.ELECTION_MODE:
                self.serverState = State.BULLY_INITIATED_MODE
                toSend = {
                    "message_type": MsgType.BULLY_ANSWER,
                    "ip": self.ip
                }
                
                self.executor.submit(self.contact_another_server, parsedItem['ip'], URI="/server_controller", req="POST", dataToSend=json.dumps(toSend))

                flag = True
                for x in self.servers_list:
                    if x > self.ip:
                        flag = False
                        toSend = {
                            "message_type": MsgType.BULLY_ELECTION,
                            "ip": self.ip
                        }
                        self.executor.submit(self.contact_another_server, x, URI="/server_controller", req="POST", dataToSend=json.dumps(toSend))
                
                # This is only for Last Server with Highest IP
                if flag:
                    self.leader_server = self.ip
                    self.serverState = State.SERVING_MODE
                    self.electionProcess = False
                    toSend = {
                        "message_type": MsgType.BULLY_COORDINATOR,
                        "ip": self.ip
                    }
                    if self.lastSentMessage != toSend:
                        self.propagate_to_all_servers(URI="/server_controller", req="POST", dataToSend=json.dumps(toSend))
                    self.lastSentMessage = toSend

        elif parsedItem['message_type'] == MsgType.BULLY_ANSWER:
            if self.serverState == State.BULLY_INITIATED_MODE:
                self.myLogger.addToQueue("Waiting for Coordinator")
                self.serverState = State.BULLY_ANSWER_MODE
        elif parsedItem['message_type'] == MsgType.BULLY_COORDINATOR:
            self.leader_server = parsedItem['ip']
            self.serverState = State.SERVING_MODE
            self.electionProcess = False
            self.myLogger.addToQueue("Leader is elected :  " + str(self.leader_server))
        else:
            pass
        
        return "DONE"

    def KeepAliveCheck(self):
        time.sleep(5)
        while True:
            self.myLogger.addToQueue("Current List: " + str(self.servers_list))
            self.myLogger.addToQueue("Leader Server: " + str(self.leader_server))
            self.myLogger.addToQueue("Serving Mode: " + str(self.serverState))
            for x in self.servers_list:
                if x != self.ip:
                    dataToSend = {
                        "message_type" : MsgType.CHECK_ALIVE,
                        "ip": x
                    }
                    try:
                        res = requests.post('http://{}{}'.format(x, '/server_controller'), data=json.dumps(dataToSend), timeout=5)
                    except requests.Timeout:
                        self.myLogger.addToQueue("Timeout for " + str(x))
                    except requests.ConnectionError:
                        self.remove_server(x)
                        self.myLogger.addToQueue("Connection Error for " + str(x))
                        dataToSend = {
                            "message_type" : MsgType.REMOVE_SERVER,
                            "ip": x
                        }
                        self.propagate_to_all_servers(URI="/server_controller", req="POST", dataToSend=json.dumps(dataToSend))
                        if x == self.leader_server:
                            if self.serverState == State.SERVING_MODE:
                                self.executor.submit(self.start_election)

            time.sleep(10)
    
    def remove_server(self, ipToRemove):
        if ipToRemove in self.servers_list:
            self.servers_list.remove(ipToRemove)
    


                    


        



        

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
