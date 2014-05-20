import sys
sys.path.append('..')
from djangoapp.settings import *
import datetime
os.environ.setdefault("DJANGO_SETTINGS_MODULE","djangoapp.settings")
from ws4redis.redis_store import RedisMessage
from ws4redis.publisher import RedisPublisher
from djangoapp.vmtemplates.ivic_portal import *
import time
import subprocess
import random
from queue import RunItem

def getPort():  
    pscmd = "netstat -ntl |grep -v Active| grep -v Proto|awk '{print $4}'|awk -F: '{print $NF}'"  
    procs = os.popen(pscmd).read()  
    procarr = procs.split("\n")
    pos = [20000,30000,40000,50000]
    i = random.randint(0,3)
    ii = 0
    al = 0
    while True:
        ii = ii +1
        tt= random.randint(pos[i],pos[i]+10000)  
        if tt not in procarr:  
            return tt
        if ii == 10:
            i = random.randint(0,3)
            ii = 0
        al = al + 1
        if al == 40000:
            return None

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
    vcluster = sessionid+"+"+template
    msg = "2 "+template #2 Creating vCluster...
    sendToClient(sessionid, msg)
    ## create VCluster
    vtemp = getVMTempID(template)
    operator = ivicSpider()
    operator.createVCluster(vcluster, vtemp)
    time.sleep(2)
    vcid = getVClusterID(vcluster)
    status = getVCStatus(vcid)
    if status == 'invalid':
        msg = "-1 "+template
        sendToClient(sessionid, msg)
        return None
    else:
        while status != 'stopped':
            if status == 'deploying':
               msg = "3 "+template
               sendToClient(sessionid, msg)
            time.sleep(1)
            status = getVCStatus(vcid)
    ## vCluster ready, start up.
    operator.startVCluster(vcid)
    vmid = getVMIID(vcid)
    status = getVMStatus(vmid)
    if status == 'invalid':
        msg = "-1 "+template
        sendToClient(sessionid, msg)
        return None
    else:
        while status != 'running':
            if status == 'starting':
               msg = "4 "+template
               sendToClient(sessionid, msg)
            time.sleep(1)
            status = getVCStatus(vmid)

    msg = "5 "+template #5 Start VNC Client
    sendToClient(sessionid, msg)
    vmport = operator.getVMPort(vmid)
    PPP = startProxy(vmport)
    proxy = PPP['proxy']
    port = PPP['port']
    process = PPP['process']
    time.sleep(2)# Change this to get better experience
    msg = "6 "+template #6 Ready
    sendToClient(sessionid, msg)
    msg =  template + " http://" + proxy + ":" + str(port) +"/vnc.html"
    proxy_url = "http://" + proxy + ":" + str(port) +"/vnc.html"
    print msg
    sendToClient(sessionid, msg)
    run = RunItem(sessionid = sessionid, template = template, proxy_url = proxy_url, proxy_process = process, vcid = vcid)
    return run

def dodown(d, proxy_process, vcid):
    if d is not None:
        log('Processing DOWN request: ' + d.string())
    proxy_process.terminate()
    operator = ivicSpider()
    operator.stopVCluster(vcid)
    status = getVCStatus(vcid)
    if status == 'invalid':
        return -1
    else:
        while status != 'stopped':
            time.sleep(1)
            status = getVCStatus(vcid)
    operator.undeployVCluster(vcid)
    return 1

'''
    status1 = getVCStatus(vcid)
    status2 = getVMStatus(vmid)
    secs = 0
    if status1 == 'invalid':
        return -1
    else:
        while status2 != 'stopped' and status1 != 'stopped':
            time.sleep(1)
            status1 = getVCStatus(vcid)
    	    status2 = getVMStatus(vmid)
            print status1, status2
            secs +=1
        #possibly, when down req arrives, the machine hasn't set up
            if secs == 60:
                operator.stopVCluster(vcid)
                secs = 0
'''




def startProxy(vmport):
    # TODO:Better proxy choosing algorithm
    proxy = PROXY
    port = getPort()
    cmd = PROXY_APP + " --vnc "+vmport['url'] +":"+str(vmport['port']) + " --listen "+str(port)
    print cmd
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    return {'proxy':proxy,'port':port,'process':process}
