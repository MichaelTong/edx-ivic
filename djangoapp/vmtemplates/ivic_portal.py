import urllib2, cookielib, urllib
import MySQLdb
from djangoapp.settings import *

def coniVICdb(host, user, passwd, port, db):
    '''
    Connect to the mysql db server on IVIC portal.
    '''
    try:
        conn = MySQLdb.connect(host=host, user = user, passwd = passwd, port = port,  db = db)
        return conn
    except Exception, e:
        print e
        return None

def getVCStatus(vcid):
    try:
        conn = coniVICdb(IVIC_DB_HOST, IVIC_DB_USER, IVIC_DB_PASSWD, IVIC_DB_PORT, 'ivic_portal')
    except Exception, e:
        print e
        return None
    try:
        cur = conn.cursor()
        sql = "SELECT status FROM virtual_cluster_instances WHERE id = '"+ str(vcid) +"'"
        cur.execute(sql)
        result = cur.fetchone()
        status = result[0]
        conn.close()
        return status
    except Exception, e:
        print e
        return None

def getVMStatus(vmid):
    try:
        conn = coniVICdb(IVIC_DB_HOST, IVIC_DB_USER, IVIC_DB_PASSWD, IVIC_DB_PORT, 'ivic_portal')
    except Exception, e:
        print e
        return None
    try:
        cur = conn.cursor()
        sql = "SELECT status FROM virtual_machine_instances WHERE id = '"+ str(vmid) +"'"
        cur.execute(sql)
        result = cur.fetchone()
        status = result[0]
        conn.close()
        return status
    except Exception, e:
        print e
        return None

def getVMTempID(template):
    '''
    Use uuid to get id of template.
    '''
    try:
        conn = coniVICdb(IVIC_DB_HOST, IVIC_DB_USER, IVIC_DB_PASSWD, IVIC_DB_PORT, 'ivic_portal')
    except Exception, e:
        print e
        return None
    try:
        cur = conn.cursor()
        sql = "SELECT id FROM vm_temps WHERE uuid = '" + template + "'"
        cur.execute(sql)
        result = cur.fetchone()
        i = result[0]
        print "Template(%s), id:%d" % (template, i)
        conn.close()
        return i
    except Exception, e:
        print e
        return None

def getVClusterID(name):
    '''
    Use name to get id of vcluster.
    The name should be unique, since we use the sessionid to create the vcluster
    and only allow each session to launch only one vm=vcluster.
    '''
    try:
        conn = coniVICdb(IVIC_DB_HOST, IVIC_DB_USER, IVIC_DB_PASSWD, IVIC_DB_PORT, 'ivic_portal')
    except Exception, e:
        print e
        return None
    try:
        cur = conn.cursor()
        sql = "SELECT id FROM virtual_cluster_instances WHERE name = '" + name + "' and status != 'invalid'"
        cur.execute(sql)
        result = cur.fetchone()
        if result is None:
            return None
        i = result[0]
        print "Name(%s), id:%d" % (name, i)
        conn.close()
        return i
    except Exception, e:
        print e
        return None

def getVMIID(vcid):
    '''
    After create vcluster, we can use vcluster id to get the id of vms.
    In current case, each vcluster contains one vm, so the result will be unique.
    '''
    try:
        conn = coniVICdb(IVIC_DB_HOST, IVIC_DB_USER, IVIC_DB_PASSWD, IVIC_DB_PORT, 'ivic_portal')
    except Exception, e:
        print e
        return None
    try:
        cur = conn.cursor()
        sql = "SELECT id FROM virtual_machine_instances WHERE virtual_cluster_instance_id = '" + str(vcid) + "' and status != 'invalid'"
        cur.execute(sql)
        result = cur.fetchone()
        if result is None:
            return None
        i = result[0]
        print "VMCluster(%d), id:%d" % (vcid, i)
        conn.close()
        return i
    except Exception, e:
        print e
        return None

# Spider-like methods to operate on portal page.

class ivicSpider():
    '''
    Use the db interface to get ids first.
    '''
    def __init__(self):
        self.spider = urllib2
        cookie_support= self.spider.HTTPCookieProcessor(cookielib.LWPCookieJar())
        opener = self.spider.build_opener(cookie_support, urllib2.HTTPHandler)
        self.spider.install_opener(opener)
        #load the page once first to get the authenticity_token
        result = self.spider.urlopen(IVIC_PORTAL_URL).read()
        temp = result[result.find("authenticity_token"):]
        temp2 = temp[temp.find("value")+7:]
        self.token = temp2[:44]
        self.login()

    def login(self):
        # Login
        postdata = urllib.urlencode({'authenticity_token':self.token, 'username':IVIC_PORTAL_USER,'password':IVIC_PORTAL_PASSWD})
        # TODO: if any change on portal, edit here
        login_url = IVIC_PORTAL_URL + '/account/signin'
        req = self.spider.Request(url = login_url, data = postdata)
        result = self.spider.urlopen(req).read()
        # print result

    def createVCluster(self, sessionid, vmtemp):
        '''
        Operate on the web page.
        vmtemp should be the id of template stored in the ivic-portal database.
        So, call getVMTempID(template) first.
        '''
        self.login()
        postdata = urllib.urlencode({'authenticity_token':self.token,'name':sessionid,'vmtemp':vmtemp,'count':1,'description':''})
        create_url = IVIC_PORTAL_URL + '/vcluster/do_create_vcluster'
        req = self.spider.Request(url = create_url, data = postdata)
        result = self.spider.urlopen(req).read()

    def startVCluster(self, vcid):
        self.login()
        start_url =  IVIC_PORTAL_URL + '/vcluster/start/' + str(vcid)
        self.spider.urlopen(start_url)

    def stopVCluster(self, vcid):
        self.login()
        stop_url =  IVIC_PORTAL_URL + '/vcluster/stop/' + str(vcid)
        self.spider.urlopen(stop_url)

    def undeployVCluster(self, vcid):
        self.login()
        undeploy_url =  IVIC_PORTAL_URL + '/vcluster/undeploy/' + str(vcid)
        self.spider.urlopen(undeploy_url)

    def getVMPort(self, vmid):
        self.login()
        console_url = IVIC_PORTAL_URL+'/vmis/console/' + str(vmid)
        result = self.spider.urlopen(console_url).read()
        first = result.find('<a href="vnc://')+15        
        temp = result[first:]
        end = temp.find('>')-1
        urlport = temp[:end]
        s = urlport.find(':')
        url = urlport[:s]
        pp = urlport[s+1:]
        if pp == '':
           port = 5900
        else:
           port = 5900 + int(pp)
        return {'url':url, 'port':port}

