#cd /home/mininet/Desktop/Distributed-System/Lab_Excercises/Lab1/skeleton/server

# coding=utf-8
import argparse
import json
import sys
from threading import Lock, Thread
import time
import traceback
import bottle
from bottle import Bottle, request, template, run, static_file, redirect
import requests
import Queue
import time
import concurrent.futures
import datetime
# ------------------------------------------------------------------------------------------------------
class Logger:
    
    def __init__(self, serverIP):
        self.fileName = serverIP+".txt"
        self.filePtr = open(self.fileName, "w+")
        self.lock = Lock()
        self.queue = Queue.Queue(100)
        thread = Thread(target=self.consume)
        thread.start()

    def writeToFile(self, item):
        self.filePtr.write(str(item["time"]) + ": " + item["text"] + "\n")
        self.filePtr.flush()

    
    def addToQueue(self, text):
        with self.lock:
            datetime_object = datetime.datetime.now()
            self.queue.put({"text": text, "time": datetime_object})

    def consume(self):
        while True:
            with self.lock:
                while not self.queue.empty():
                    item = self.queue.get()
                    self.writeToFile(item)
            time.sleep(1)

    

    

        

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


# ------------------------------------ ------------------------------------------------------------------
class Server(Bottle):

    def __init__(self, ID, IP, servers_list):
        super(Server, self).__init__()
        self.blackboard = Blackboard()
        self.id = int(ID)
        self.ip = str(IP)
        self.servers_list = servers_list
        # print(servers_list)
        self.myLogger = Logger(self.ip)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

        # list all REST URIs
        # if you add new URIs to the server, you need to add them here
        self.route('/', callback=self.index)
        self.get('/board', callback=self.get_board)
        self.get('/board/alldata',callback=self.get_board_data)
        self.get('/serverlist', callback=self.get_serverlist)
        
        self.post('/', callback=self.post_index)
        self.post('/board', callback=self.post_board)
        self.post('/propagate', callback=self.post_propagate)
        self.post('/board/<number:int>/', callback=self.post_board_ID)
        self.post('/propagate_deletemodify', callback=self.post_propagate_deletemodify)
        # we give access to the templates elements
        self.get('/templates/<filename:path>', callback=self.get_template)
        # You can have variables in the URI, here's an example
        # self.post('/board/<element_id:int>/', callback=self.post_board) where post_board takes an argument (integer) called element_id


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
                f = requests.Session()
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
        newEntry = request.forms.get('entry')
        self.myLogger.addToQueue('post_board: ' + newEntry)
        leader_server = self.get_leader_server()
        if self.ip == leader_server:
            addedItem = self.blackboard.add_content(newEntry)
            self.propagate_to_all_servers(URI="/propagate", req="POST", dataToSend=json.dumps(addedItem))
        else:
            payload = {
                'entry': newEntry,
            }
            self.contact_another_server(leader_server, URI='/board', req="POST", dataToSend=payload)
            redirect('/')

        

        

    # post on ('/board/<number>)
    def post_board_ID(self, number):
        option = request.forms.get('delete')
        modified_entry = request.forms.get('entry')

        if option == "1":
            self.myLogger.addToQueue('DELETE : ' + str(number))
        else:
            self.myLogger.addToQueue('MODIFY : ' + str(number) + " => " + modified_entry)

        leader_server = self.get_leader_server()
        if leader_server == self.ip:
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
            self.contact_another_server(leader_server, URI='/board/{0}/'.format(number), req="POST", dataToSend=payload)


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



        

    # post on ('/')
    def post_index(self):
        try:
            # we read the POST form, and check for an element called 'entry'
            new_entry = request.forms.get('entry')
        except Exception as e:
            print("[ERROR] "+str(e))


    def get_template(self, filename):
        return static_file(filename, root='./server/templates/')

    
    # Getting the leader server
    def get_leader_server(self):
        leader = min(self.servers_list)
        return leader

        

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
