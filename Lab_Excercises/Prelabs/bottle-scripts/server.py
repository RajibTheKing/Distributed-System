import sys
import json as JsonParser
from bottle import route, run, get, post, request


@route('/hello')
def hello():
    return "Hello World!"

@route('/')
def home():
    return "I am in the home page"

@post('/input') # or @route('/input', method='POST')
def input():
    try:
        dictData = request.json # This returns Dictionary Data
        print(dictData)
        for x in dictData:
            print(x + ": " + dictData[x])

        return dictData
    except:
        return "Error"
    

run(host='localhost', port=8080, debug=True)

