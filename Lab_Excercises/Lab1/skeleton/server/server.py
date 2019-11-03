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
# ------------------------------------------------------------------------------------------------------

class Blackboard():

    def __init__(self):
        self.content = [{"id": 1, "entry": "First"}, {"id": 2, "entry": "Second"}]
        self.lock = Lock() # use lock when you modify the content


    def get_content(self):
        with self.lock:
            cnt = self.content
        return cnt

    def add_content(self, new_content):
        with self.lock:
            l = len(self.content)
            if l == 0:
                lastID = 0
            else:
                lastID = self.content[l-1]["id"]
            
            self.content.append({"id": lastID+1, "entry": new_content})

    def set_content(self,number, modified_entry):
        with self.lock:
            self.content = list(map(lambda x: {"id": number, "entry": modified_entry} if x['id'] == number else x ,self.content))
            
    
    def delete_content(self, number):
        with self.lock:
            self.content = list(filter(lambda x: x['id']!=number,self.content))


# ------------------------------------ ------------------------------------------------------------------
class Server(Bottle):

    def __init__(self, ID, IP, servers_list):
        super(Server, self).__init__()
        self.blackboard = Blackboard()
        self.id = int(ID)
        self.ip = str(IP)
        self.servers_list = servers_list
        print(servers_list)
        # list all REST URIs
        # if you add new URIs to the server, you need to add them here
        self.route('/', callback=self.index)
        self.get('/board', callback=self.get_board)
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
                #res = requests.post('http://{}{}'.format(srv_ip, URI), data=json.dumps({"entry": newValue}))
                print(res)

            elif 'GET' in req:
                res = requests.get('http://{}{}'.format(srv_ip, URI))
            # result can be accessed res.json()
            if res.status_code == 200:
                success = True
        except Exception as e:
            print("[ERROR] "+str(e))
        return success


    def propagate_to_all_servers(self, URI, req='POST', dataToSend=None):
        for srv_ip in self.servers_list:
            if srv_ip != self.ip: # don't propagate to yourself
                self.do_parallel_task(self.contact_another_server, args=(srv_ip, URI, req, dataToSend))

                #success =  self.contact_another_server(srv_ip, URI, req, dataToSend)
                #if not success:
                #    print("[WARNING ]Could not contact server {}".format(srv_ip))


    # route to ('/')
    def index(self):
        # we must transform the blackboard as a dict for compatiobility reasons
        boardData = self.blackboard.get_content()
        board = dict()
        for x in boardData :
           board[x["id"]] = x["entry"]
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
        for x in boardData :
           board[x["id"]] = x["entry"]
        return template('server/templates/blackboard.tpl',
                        board_title='Server {} ({})'.format(self.id,
                                                            self.ip),
                        board_dict=board.iteritems())

    # post on ('/board') add new entry
    def post_board(self):
        print(dir(request))
        print(request.forms)
        print(list(request.forms))
        newEntry = request.forms.get('entry')
        leader_server = self.get_leader_server()
        if self.ip == leader_server:
            print(newEntry)
            self.blackboard.add_content(newEntry)
            #def propagate_to_all_servers(self, URI, req='POST', params_dict=None):
            self.propagate_to_all_servers(URI="/propagate", req="POST", dataToSend=json.dumps({"entry": newEntry}))
        else:
            payload = {
                'entry': newEntry,
            }
            self.contact_another_server(leader_server, URI='/board', req="POST", dataToSend=payload)
            redirect('/')

        

        

    # post on ('/board/<number>)
    def post_board_ID(self, number):
        print(request)
        print("I am inside /board/<number>")
        print(number)
        option = request.forms.get('delete')
        modified_entry = request.forms.get('entry')
        print(option)
        leader_server = self.get_leader_server()
        if leader_server == self.ip:
            if option == "1":
                print("deleting content id {0}",number)
                self.blackboard.delete_content(number)
                self.propagate_to_all_servers(URI="/propagate_deletemodify", req="POST", dataToSend=json.dumps(
                    {
                        "value": option, 
                        "number": number
                    }))
                
            else:
                print("modifying content id {0}",number)
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
        print(list(request.body))
        data = list(request.body)
        print(json.loads(data[0]))
        parsed = json.loads(data[0])

        self.blackboard.add_content(parsed['entry'])
    
    # post on ('/propagate_deletemodify/)
    def post_propagate_deletemodify(self):
        print(list(request.body))
        data = list(request.body)
        print(json.loads(data[0]))
        parsed = json.loads(data[0])
        option = parsed['value']
        if option == "1":
            number = parsed['number']
            print("deleting content id {0}",number)
            self.blackboard.delete_content(number)
        else:
            number = parsed['number']
            modified_entry = parsed['entry']
            print("modifying content id {0}",number)
            self.blackboard.set_content(number,modified_entry)



        

    # post on ('/')
    def post_index(self):
        try:
            # we read the POST form, and check for an element called 'entry'
            new_entry = request.forms.get('entry')
            print("Received: {}".format(new_entry))
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
