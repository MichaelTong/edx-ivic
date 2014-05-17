#!/usr/bin/env python
import thread
import multiprocessing
import signal
from handler import *
from utils import shutdown
from multiprocessing.connection import Client

def sigint_handler(signum, frame):
    global is_sigint_up
    is_sigint_up = True
    print 'Catch interrupt signal'

signal.signal(signal.SIGINT, sigint_handler)

is_sigint_up = False

if __name__ == '__main__':
    cpu_num = multiprocessing.cpu_count()
    listen_thread = listen()
    queue_thread = []
    
    i = 1
    while i <= cpu_num:
        t = queue_handler(i)
        queue_thread.append(t)
        t.start()
        i = i + 1

    listen_thread.start()
    print "Quit the application with CONTROL-C"
    while True:
        try:
            if is_sigint_up:
                listen_thread.stop()
                i = 1
                while i <= cpu_num:
                    queue_thread[i-1].stop()
                    i = i + 1
                shutdown()
                exit()
        except Exception, e:
            break
    
