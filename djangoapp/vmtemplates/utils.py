from multiprocessing.connection import Client
from models import VMTemplate
from djangoapp.settings import *
from django.db import models
from django.contrib.auth.models import User
import datetime
import hashlib
import paramiko
from scp import SCPClient
import os
import thread  
import sys

def sentToQueue(item):
    address = ('localhost',int(QUEUE_PORT))
    conn = Client(address, authkey = AUTHKEY)
    conn.send(item)
    conn.close()

def makeUrl(method,vstore):
    if method == 'nfsmount':
        deploy_url = 'nfs://'+vstore+'/var/lib/ivic/www/vstore/nfsbase/'
        cowdir = 'nfs://'+vstore+'/var/lib/ivic/www/vstore/nfscow'
    return {'deploy_url':deploy_url, 'cowdir':cowdir}

# get data in form.
def loadFromRequest(request):
    image = request.POST.get('image')
    name = request.POST.get('name')
    description = request.POST.get('description')
    capabilities = request.POST.get('capabilities')
    os_type = request.POST.get('os_type')
    distribution = request.POST.get('distribution')
    release = request.POST.get('release')
    kernel = request.POST.get('kernel')
    packages = request.POST.get('packages')
    repository = request.POST.get('repository')
    m = request.POST.get('memory')
    try:
        memory = int(m)
    except:
        memory = 0
    d = request.POST.get('disk')
    try:
        disk = int(d)
    except:
        disk = 0
    newconfig = request.POST.get('newconfig')
    deploy_method = request.POST.get('method')
    deploy_vstore = request.POST.get('vstore')
    create_user = request.user
    return {'image':image,'name':name,'description':description,'capabilities':capabilities,'os_type':os_type,'distribution':distribution,'release':release,'kernel':kernel,'packages':packages,'repository':repository,'memory':memory,'disk':disk, 'newconfig':newconfig,'deploy_method':deploy_method,'deploy_vstore':deploy_vstore,'create_user':create_user}

# use XML information and username to get hash code, used as the xml file name
def hashFilename(dict):
    dict_str = dict.copy()
    dict_str['create_user'] = dict['create_user'].username
    del dict_str['deploy_vstore']
    del dict_str['image']
    obj = hashlib.md5()
    obj.update(str(dict_str))
    hash = obj.hexdigest()
    filename = hash[0:8]+'-'+hash[8:12]+'-'+hash[12:16]+'-'+hash[16:20]+'-'+hash[20:32]
    return filename

def exsit(filename):
    try:
         t = VMTemplate.objects.get(filename = filename)
         if t is not None:
              return True
         return False
    except:
         return False

def createNew(dict, filename):
    try:
        new_tp = VMTemplate.objects.create(name = dict['name'], description = dict['description'], capabilities = dict['capabilities'], os_type = dict['os_type'], distribution = dict['distribution'], release = dict['release'], kernel = dict['kernel'], packages = dict['packages'], repository = dict['repository'], memory = dict['memory'], disk = dict['disk'], deploy_method = dict['deploy_method'], deploy_url = dict['deploy_url'], cowdir = dict['cowdir'] ,create_user = dict['create_user'], filename = filename)
        new_tp.dumps()
        server = dict['deploy_vstore']
        localFile = os.path.join(LOCAL_XML_DIR, filename+'.xml')
        # if not use nfs, uncomment the followings
        #remoteFile = '/var/lib/ivic/vstore/template/' + filename + '.xml'
    	#thread.start_new_thread(sendFile, (localFile, remoteFile, server, 22, VSTORE_USERNAME, VSTORE_PASSWD))  
        image = dict['image']
        thread.start_new_thread(transferImage, (image, filename, server, 22, VSTORE_USERNAME, VSTORE_PASSWD))
        return new_tp
    except Exception,e:
        print e
        return None

def createSSH(server, port , username, passwd, timeout = 10):
    try:
        s = paramiko.SSHClient()
        s.load_system_host_keys()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        s.connect(server, port, username, passwd, timeout = timeout)
        return s
    except Exception,e:
        print e
        return None

def createSCP(server, port , username, passwd):
    try:
        c = createSSH(server, port, username, passwd)
        s = SCPClient(c.get_transport())
        return (c, s)
    except Exception, e:
        print e
        return None

def sendFile(localFile, remoteFile, server, port, username, passwd):
    try:
        c, s = createSCP(server, port, username, passwd)
        s.put(localFile, remoteFile)
        c.close()
        print 'File send to %s\tOK\n'%(server)
    except Exception, e:
        print e
        print 'Local file %s send to %s\tFailed\n'%(localFile,server)

def remoteCmd(server, port, username, passwd, Cmds):
    try:
        c = createSSH(server, port, username, passwd)
        for cmd in Cmds:
            stdin, stdout, stderr = c.exec_command(cmd)
            out = stdout.readlines()
            err = stderr.readlines()
            for o in out:
                sys.stdout.write(o)
            for e in err:
                sys.stderr.write(e)
        print '%s\tOK\n'%(server)
        c.close()
    except:
        print '%s\tError\n'%(server)

def delLocal(filepath):
    os.system('rm '+filepath)

def delRemote(filepath, server, port, username, passwd):
    cmd = 'rm '+filepath
    remoteCmd(server, port, username, passwd, [cmd])

def getImages():
# we have mounted the remote dir
    d = os.path.join(BASE_DIR, 'imgs')
    return os.listdir(d)

# if get from remote, use as below
'''
    try:
        c = createSSH(IMG_STORE, 22, IMG_USERNAME, IMG_PASSWD)
        cmd = 'ls ' + IMG_DIR
        stdin, stdout, stderr = c.exec_command(cmd)
        out = stdout.readlines()
        err = stderr.readlines()
        for o in out:
            o = o[0:o.find('\n')]
        for e in err:
            sys.stderr.write(e)
        c.close()
        print 'Get Images from %s\tOK\n'%(IMG_STORE)
        return out
    except Exception, e:
        print e
        print 'Get Images from %s\tFailed\n'%(IMG_STORE)
        return []
'''
def transferImage(image, filename, server, port, username, passwd):
    # TODO: Now the image store is the same as vstore.
    #       Only do copy.
    try:
        if server == IMG_STORE:
            c = createSSH(IMG_STORE, 22, IMG_USERNAME, IMG_PASSWD)
            if image.find('\n') != -1:
                image = image[0:image.find('\n')]
            if image.find('\r') != -1:
                image = image[0:image.find('\r')]
            origin = os.path.join(IMG_DIR, image)
            target = '/var/lib/ivic/www/vstore/nfsbase/' + filename +'.img'
            cmd = 'cp ' + origin + ' '+ target
            print cmd
            stdin, stdout, stderr = c.exec_command(cmd)
            out = stdout.readlines()
            err = stderr.readlines()
            for o in out:
                sys.stdout.write(o)
            for e in err:
                sys.stderr.write(e)
            c.close()
            print 'Transfer images to %s\tOK\n'%(server)
    except Exception, e:
        print e
        print 'Transfer images to %s\tFailed\n'%(server)

 

        
