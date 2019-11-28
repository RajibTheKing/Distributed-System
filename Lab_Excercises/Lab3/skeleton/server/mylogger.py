
from allimports import *

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