import argparse
import json
import sys
from threading import Lock, Thread
import time
import traceback
import bottle
from bottle import Bottle, request, template, run, static_file, redirect
import requests
import random
import concurrent.futures


class UnitTest:

    def __init__(self, ip):
        self.serverIP = ip
        self.serverList = None
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=20)
    
    def do_parallel_task(self, method, args=None):
        thread = Thread(target=method,
                        args=args)
        thread.daemon = True
        thread.start()

    def get_servers_list(self):
        response = self.sendRequest(self.serverIP, URI='/serverlist', req="GET")
        print(response.content)

        self.serverList = json.loads(response.content)
        print(self.serverList)

    def sendRequest(self, srv_ip, URI, req='POST', dataToSend=None):
        # Try to contact another serverthrough a POST or GET
        # usage: server.contact_another_server("10.1.1.1", "/index", "POST", params_dict)
        success = False
        try:
            if 'POST' in req:
                print(srv_ip + " Sending Request POST: " + URI + " param: " + str(dataToSend))
                f = requests.Session()
                res = requests.post('http://{}{}'.format(srv_ip, URI), data=dataToSend )
                
                #res = requests.post('http://{}{}'.format(srv_ip, URI), data=json.dumps({"entry": newValue}))
                if res.status_code == 200:
                    print(srv_ip + " Got success for " + str(dataToSend))
                else:
                    print("FAILED!! status_code = " + str(res.status_code))
                return res

            elif 'GET' in req:
                print("sending get request")
                res = requests.get('http://{}{}'.format(srv_ip, URI))
                return res
            else:
                print("Unexpected condition")

        except Exception as e:
            print("Found Error --> ZAKEE")
            print("[ERROR] "+str(e))
        return success

    def getRandomText(self):
        numberOfChars = random.randint(1,10)
        randText = ""
        for x in range(numberOfChars):
            val = random.randint(1,26) + 65
            randText += chr(val)
        return randText

    """scene 1 client connect to all servers and send 5 messages concurrently """
    def generate_Scenario1(self):
        for server in self.serverList:
            print("Check: " + server)
            for i in range(5):
                newEntry = "text_" + self.getRandomText()
                URI = '/board'
                req = 'POST'
                payload = {
                    'entry': newEntry,
                }
                dataToSend = payload
                self.executor.submit(self.sendRequest, server, URI, req, dataToSend)
                #self.do_parallel_task(self.sendRequest, args=(server, URI, req, dataToSend))
                #time.sleep(0.010)
                # self.contact_another_server(srv_ip, URI, req, dataToSend)
                #res = self.sendRequest(server,URI,req,dataToSend)
                print(newEntry)
            print("\n\n")
    
    
    def generate_Scenario2(self):
        self.generate_Scenario1()
        # time.sleep(1)
        for server in self.serverList:
            print("Check: " + server)
            
            modifiedEntry = "modified_text_" + self.getRandomText()
            URI = '/board/14/'
            req = 'POST'
            payload = {
                'entry': modifiedEntry,
            }
            dataToSend = payload
            self.executor.submit(self.sendRequest, server, URI, req, dataToSend)
            print("\n\n")
        
        time.sleep(20)

        # get value from server 4 and 7 
        res4 = self.sendRequest(srv_ip='10.1.0.4',URI='/board/alldata',req='GET')
        res7 = self.sendRequest(srv_ip='10.1.0.7',URI='/board/alldata',req='GET')
        

        if res4.content == res7.content:
            print("got same response from server 4 and 7 ")
        else:
            print("MISMATCH FOUND!!!!")

def main():
    test = UnitTest('10.1.0.2')
    test.get_servers_list()
    test.generate_Scenario2()

if __name__ == '__main__':
    main()

