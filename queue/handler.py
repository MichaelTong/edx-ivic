
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
RunQueue = Queue()
reqlock = thread.allocate_lock()
downlock = thread.allocate_lock()
runlock = thread.allocate_lock()


def msg_handler(msg):
    if msg['ex'] == 'SHUTSELF':
        return
    if msg['method'] == 'UP':
        sessionid = msg['sessionid']
        template = msg['template']
        r = ReqItem(sessionid, template)
        reqlock.acquire()
        ReqQueue.enqueue(r)
        reqlock.release()
        # TODO: Tell the client now queuing
    if msg['method'] == 'DOWN':
        sessionid = msg['sessionid']
        template = msg['template']
        proxy = msg['proxy']
        port = msg['port']
        vm = msg['vm']
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
            finally:
               conn.close()
        conn.close()
        listener.close()

    def stop(self):
        self.thread_stop = True
        log('Stopped listener thread')
        conn = Client(self.address, authkey = AUTHKEY)
        conn.send({'ex':'SHUTSELF'})
        conn.close()
        

class queue_handler(threading.Thread):
    def __init__(self, id):
        threading.Thread.__init__(self)
        self.id = id
        self.thread_stop = False
    
    def run(self):
        log("Started queue handler thread #" + str(self.id))
        while not self.thread_stop:
            reqlock.acquire()
            if not ReqQueue.is_empty():
                r = ReqQueue.dequeue()
            else:
                r = None
            reqlock.release()
            if r is not None:
                doreq(r)
            # TODO: Record in RunQueue
            #       Tell the client now Running
            #       Redirect to noVNC page
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
