import sys
sys.path.append('..')
from djangoapp.settings import *
import datetime
def log( msg, arg = '' ):
    if DEBUG:
        now = datetime.datetime.now()
        out = '[' + now.strftime('%d/%B/%Y %H:%M:%S') + '] ' + msg
        print out, arg

def doreq(r):
    # TODO: 1. Tell the client the procedure
    #       2. Remote control proxy and ivic
    log('Process up request: ' + r.string())
    return 'ok'

def dodown(d):
    log('Processing down request: ' + d.string())
    return 'ok'

def shutdown():
    log('Shutting down all the running VMs...')
    return 'ok'

 
