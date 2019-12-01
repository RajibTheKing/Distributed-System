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
import colorama
from colorama import Fore, Style


class UnitTest:

    def __init__(self, ip):
        self.serverIP = ip
        self.serverList = None
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=20)
    
    

    def get_servers_list(self):
        response = self.sendRequest(self.serverIP, URI='/serverlist', req="GET")
        self.serverList = json.loads(response.content)
        print(Style.BRIGHT + Fore.YELLOW + str(self.serverList))

    def sendRequest(self, srv_ip, URI, req='POST', dataToSend=None):
        # Try to contact another serverthrough a POST or GET
        # usage: server.contact_another_server("10.1.1.1", "/index", "POST", params_dict)
        success = False
        try:
            if 'POST' in req:
                print(Fore.CYAN + srv_ip + " Sending Request POST: " + URI + " param: " + str(dataToSend))
                f = requests.Session()
                res = requests.post('http://{}{}'.format(srv_ip, URI), data=dataToSend )
                
                #res = requests.post('http://{}{}'.format(srv_ip, URI), data=json.dumps({"entry": newValue}))
                if res.status_code == 200:
                    print(Fore.GREEN + srv_ip + " Got success for " + str(dataToSend))
                else:
                    print(Fore.RED + "FAILED!! status_code = " + str(res.status_code))
                return res

            elif 'GET' in req:
                print(Fore.CYAN + "sending request to server " +str(srv_ip))
                res = requests.get('http://{}{}'.format(srv_ip, URI))
                return res
            else:
                print(Fore.RED + "Unexpected condition")

        except Exception as e:
            print(Fore.RED + "[ERROR] "+str(e))
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
                
    
    
    def generate_Scenario2(self):
        print(Style.BRIGHT + Fore.CYAN + "Sending 5 messages concurrently to all the servers")
        self.generate_Scenario1()
        for server in self.serverList:
            modifiedEntry = "modified_text_" + self.getRandomText()
            URI = '/board/14/'
            req = 'POST'
            payload = {
                'entry': modifiedEntry,
            }
            dataToSend = payload
            self.executor.submit(self.sendRequest, server, URI, req, dataToSend)
            
        
        time.sleep(40)

        # get value from server 4 and 7 
        print(Style.BRIGHT + Fore.CYAN + "----------------------------------------------------------------")
        print(Style.BRIGHT + Fore.CYAN + "Requesting data from server 4 and 7")
        res4 = self.sendRequest(srv_ip='10.1.0.4',URI='/board/alldata',req='GET')
        res7 = self.sendRequest(srv_ip='10.1.0.7',URI='/board/alldata',req='GET')
        
        data4 = json.loads(res4.content)
        data7 = json.loads(res7.content)

        for (x,y) in zip(data4,data7):
            if data4[x] != data7[y]:
                print("MISMATCH!! " + str(x) + " and " + str(y))
        

        if res4.content == res7.content:
            print(Style.BRIGHT + Fore.GREEN + "got same response from server 4 and 7 ")
            print(Style.BRIGHT + Fore.GREEN + "Scenario 2 success")
        else:
            print(Fore.RED + "MISMATCH FOUND!!!!")

def main():
    colorama.init(autoreset=True)
    test = UnitTest('10.1.0.2')
    test.get_servers_list()
    test.generate_Scenario1()

if __name__ == '__main__':
    main()

