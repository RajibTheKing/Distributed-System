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

    """scene 1 client connect to all servers and send 5  random modify operations concurrently """
    def generate_DeleteScenario(self): #Not ready Yet
        res = self.sendRequest(srv_ip="10.1.0.1",URI='/board/alldata',req='GET')
        content = json.loads(res.content)
        for server in self.serverList:
            allreadySent = []
            for i in range(2):
                index = random.randint(0, len(content)-1)
                while index in allreadySent:
                    index = random.randint(0, len(content)-1)
                allreadySent.append(index)

                randomUUID = content[index]["id"]
                modifiedEntry = "modified_text_" + self.getRandomText()
                URI = '/board/'+randomUUID+'/'
                req = 'POST'
                payload = {
                    'delete': '1',
                    'entry': modifiedEntry,
                }
                dataToSend = payload
                self.executor.submit(self.sendRequest, server, URI, req, dataToSend)
                
    
 
def main():
    colorama.init(autoreset=True)
    test = UnitTest('10.1.0.2')
    test.get_servers_list()
    test.generate_DeleteScenario()

if __name__ == '__main__':
    main()

