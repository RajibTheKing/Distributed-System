# coding=utf-8
from allimports import *

# User defined modules
import distributedboard
import mylogger
from serverState import State
from myMsgType import MsgType
from vectorclock import VectorClock


# ------------------------------------ ------------------------------------------------------------------
class Server(Bottle):

    def __init__(self, ID, IP, servers_list):
        super(Server, self).__init__()
        
        self.id = int(ID)
        self.ip = str(IP)
        self.servers_list = servers_list
        self.serverIndex = self.servers_list.index(self.ip)
        self.vectorClock = VectorClock(self.serverIndex, len(self.servers_list))
        self.myLogger = mylogger.Logger(self.ip)
        self.blackboard = distributedboard.Blackboard(self.vectorClock, self.myLogger)
        
        self.queue = Queue.Queue(100)
        thread = Thread(target=self.consume)
        thread.start()
        
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

        # list all REST URIs
        # if you add new URIs to the server, you need to add them here

        # API for Clients
        self.route('/', callback=self.index)
        self.get('/board', callback=self.get_board)
        self.post('/', callback=self.post_index)
        self.post('/board', callback=self.post_board)
        self.post('/board/<number>/', callback=self.post_board_ID)
        
        # API for Scripts
        self.get('/serverlist', callback=self.get_serverlist)
        self.get('/board/alldata',callback=self.get_board_data)
        
        # API for Server Internals
        self.post('/propagate', callback=self.post_propagate)
        

        # we give access to the templates elements
        self.get('/templates/<filename:path>', callback=self.get_template)
        # You can have variables in the URI, here's an example
        # self.post('/board/<element_id:int>/', callback=self.post_board) where post_board takes an argument (integer) called element_id
        
        self.lastSentMessage = None

    def consume(self):
        while True:
            while not self.queue.empty():
                (operationType, parsedItem) = self.queue.get()
            time.sleep(1)
        

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
    def generateDataToShow(self):
        boardData = self.blackboard.get_content()
        self.myLogger.addToQueue(str(boardData))
        self.myLogger.addToQueue(str(self.vectorClock.getCurrentClock()))
        customList = []
        for x in boardData:
            customList.append((x["id"], x["entry"]))
        return customList

    def index(self):
        return template('server/templates/index.tpl',
                        board_title='Server {} ({})'.format(self.id,
                                                            self.ip),
                        board_dict=self.generateDataToShow(),
                        members_name_string='INPUT YOUR NAME HERE')
       

    # get on ('/board')
    def get_board(self):
        return template('server/templates/blackboard.tpl',
                        board_title='Server {} ({})'.format(self.id,
                                                            self.ip),
                        board_dict=self.generateDataToShow())
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

        addedItem = self.blackboard.add_content(newEntry)
        payload = {
            "Operation": "add",
            "Element" : addedItem,
        }
        self.propagate_to_all_servers(URI="/propagate", req="POST", dataToSend=json.dumps(payload))
 
        
        

    # post on ('/board/<number>)
    def post_board_ID(self, number):
        option = request.forms.get('delete')
        modified_entry = request.forms.get('entry')

        if option == "1":
            self.myLogger.addToQueue('DELETE : ' + str(number))
        else:
            self.myLogger.addToQueue('MODIFY : ' + str(number) + " => " + modified_entry)
        
        if option == "1":
            deletedItem = self.blackboard.delete_content(number)
            self.propagate_to_all_servers(URI="/propagate", req="POST", dataToSend=json.dumps(
                {
                    "Operation": "delete", 
                    "Element": deletedItem
                }))
            
        else:
            modifiedItem = self.blackboard.set_content(number,modified_entry)
            self.propagate_to_all_servers(URI="/propagate", req="POST", dataToSend=json.dumps(
                {
                    "Operation": "modify", 
                    "Element": modifiedItem
                }))
        redirect('/')


    # post on ('/propagate')
    def post_propagate(self):
        data = list(request.body)
        parsedItem = json.loads(data[0])
        self.blackboard.propagateContent(parsedItem["Operation"], parsedItem["Element"])
    
        

    # post on ('/')
    def post_index(self):
        try:
            # we read the POST form, and check for an element called 'entry'
            new_entry = request.forms.get('entry')
        except Exception as e:
            print("[ERROR] "+str(e))


    def get_template(self, filename):
        return static_file(filename, root='./server/templates/')
    
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
