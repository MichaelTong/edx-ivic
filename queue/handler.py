
import os
import sys
sys.path.append('..')
import threading
import thread
from queue import ReqItem, DownItem, RunItem
from queue import Queue
from multiprocessing.connection import Listener, Client
from djangoapp.settings import *
from utils import *

ReqQueue = Queue()
DownQueue = Queue()
RunQueue = {}
reqlock = thread.allocate_lock()
downlock = thread.allocate_lock()
runlock = thread.allocate_lock()


def msg_handler(msg):
    global ReqQueue
    global DownQueue
    global RunQueue
    global reqlock
    global downlock
    global runlock
    if msg['method'] == 'SHUTSELF':
        return
    if msg['method'] == 'UP':
        sessionid = msg['sessionid']
        template = msg['template']
        r = ReqItem(sessionid, template)
        reqlock.acquire()
        ReqQueue.enqueue(r)
        reqlock.release()
    if msg['method'] == 'DOWN':
        sessionid = msg['sessionid']
        template = msg['template']
        d = DownItem(sessionid=sessionid, template=template, vm = vm, proxy = proxy, port = port)
        downlock.acquire()
        DownQueue.enqueue(d)
        downlock.release()

class listen(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.thread_stop = False
        self.address = ('localhost',int(QUEUE_PORT))

    def run(self):
        log("Started listener thread")
        print "Listen on http://localhost:" + QUEUE_PORT
        listener = Listener(self.address, authkey = AUTHKEY)
    
        while not self.thread_stop:
            conn = listener.accept()
            log('Connection accepted from ',listener.last_accepted)
        
            msg = conn.recv()
            try:
               msg_handler(msg)
            except Exception, e:
               print e

        conn.close()
        listener.close()

    def stop(self):
        self.thread_stop = True
        log('Stopped listener thread')
        conn = Client(self.address, authkey = AUTHKEY)
        conn.send({'method':'SHUTSELF'})
        conn.close()
        

class queue_handler(threading.Thread):
    def __init__(self, id):
        threading.Thread.__init__(self)
        self.id = id
        self.thread_stop = False
    
    def run(self):
        global ReqQueue
        global DownQueue
        global RunQueue
        global reqlock
        global downlock
        global runlock
        log("Started queue handler thread #" + str(self.id))
        while not self.thread_stop:
            # get a up request
            reqlock.acquire()
            if not ReqQueue.is_empty():
                r = ReqQueue.dequeue()
            else:
                r = None
            reqlock.release()

            if r is not None:
                # check if already running
                runlock.acquire()
                condition = RunQueue.has_key((r.sessionid,r.template))
                runlock.release()
                if condition:
                    runlock.acquire()
                    proxy_url, proxy_process, vcid =RunQueue[(r.sessionid,r.template)]
                    runlock.release()
                    msg = "6 "+r.template #6 Ready
                    sendToClient(r.sessionid, msg)
                    msg =  r.template + " " + proxy_url
                    sendToClient(r.sessionid, msg)
                    r = None
                else:
                    # not running, start a vm and record into RunQueue
                    run = doreq(r)
                    RunQueue = dict(RunQueue.items() + run.dict().items())
                    print RunQueue
                    runlock.release()
            
            #get a down request
            downlock.acquire()
            if not DownQueue.is_empty():
                d = DownQueue.dequeue()
            else:
                d = None
            downlock.release()
            if d is not None:
                dodown(d)
            # TODO: Delete the record in RunQueue
    
    def stop(self):
        self.thread_stop = True
        log("Stopped queue handler thread # " + str(self.id))
