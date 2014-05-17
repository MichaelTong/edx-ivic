import sys
sys.path.append('..')
from djangoapp.settings import *
import datetime
os.environ.setdefault("DJANGO_SETTINGS_MODULE","djangoapp.settings")
from ws4redis.redis_store import RedisMessage
from ws4redis.publisher import RedisPublisher

def log( msg, arg = '' ):
    if DEBUG:
        now = datetime.datetime.now()
        out = '[' + now.strftime('%d/%B/%Y %H:%M:%S') + '] ' + msg
        print out, arg

def sendToClient(sessionid, msg):
    redis_publisher = RedisPublisher(facility='foobar', sessions=[sessionid])
    message = RedisMessage(msg)
    redis_publisher.publish_message(message)

def doreq(r):
    # TODO: 1. Tell the client the procedure
    #       2. Remote control proxy and ivic
    log('Process UP request: ' + r.string())
    sessionid = r.sessionid
    template = r.template
    redis_publisher = RedisPublisher(facility='foobar', sessions=[sessionid])
    msg = "2" #2 Applying for VM...
    sendToClient(sessionid, msg)
    vm = startVM(template)
    msg = "3" #3 Applying for Proxy...
    sendToClient(sessionid, msg)
    PP = startProxy(vm)
    proxy = PP['proxy']
    port = PP['port']
    msg = "4" #4 Ready
    sendToClient(sessionid, msg)
    return {'sessionid':sessionid,'template':template,'vm':vm,'proxy':proxy,'port':port}

def dodown(d):
    log('Processing DOWN request: ' + d.string())
    return 'ok'

def shutdown():
    log('Shutting down all the running VMs...')
    return 'ok'

def startVM(template):
    vm='192.168.1.111'
    return vm

def startProxy(vm):
    proxy = '192.168.1.112'
    port = '6080'
    return {'proxy':proxy,'port':port}
