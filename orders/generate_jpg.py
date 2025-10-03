import threading
import imgkit

class thread(threading.Thread):
    def __init__(self, thread_name, thread_ID,url,output):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.thread_ID = thread_ID
        self.url=url
        self.output=output


    def run(self):
        print(str(self.thread_name) +" "+ str(self.thread_ID));
        imgkit.from_url(self.url,self.output)
        print("done generating")
