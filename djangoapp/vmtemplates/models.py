from django.db import models
from django.contrib.auth.models import User
import datetime
import hashlib
class VMTemplate(models.Model):
# vTemplate uuid='filename'
# Name
    name = models.CharField(max_length=30, verbose_name='Name')
# Description
    description = models.CharField(max_length=50, blank=True, verbose_name='Description')
# Capabilities
    capabilities = models.CharField(max_length=30, default='<vNode/>', verbose_name='Capabilities')
# OS
    # Type
    os_type = models.CharField(max_length=30, verbose_name='OS Type')
    # Distribution
    distribution = models.CharField(max_length=30, blank=True, verbose_name='Distribution')
    # Release
    release = models.CharField(max_length=30, blank=True, verbose_name='Release')
    # Kernel
    kernel = models.CharField(max_length=30, blank=True, verbose_name='Kernel')
    # Packages
    packages = models.CharField(max_length=30, default='base-files', verbose_name='Packages')
# Repository
    repository = models.CharField(max_length=100, default='local', verbose_name='Repository')
# DeployInfo
    # PerferedSetting
        # Mem
    memory = models.IntegerField(verbose_name='Perferred Memory(MB, Only Int)')
        # DiskSize(add G)
    disk = models.IntegerField(verbose_name='Perferred Disk Size(GB, Only Int)')
    	# Config
            # newconfig
    newconfig = models.CharField(max_length=100,default='something',verbose_name='NewConfig')
    # Method
    deploy_method = models.CharField(max_length=30, default='nfsmount', verbose_name='Deploy Method')
    # URL
    deploy_url = models.CharField(max_length=200, verbose_name='Deploy URL')
    # COWDir
    cowdir = models.CharField(max_length=30, verbose_name='COWDir')

# Not In XML
    create_time = models.DateTimeField(default = datetime.datetime.now, verbose_name='Created Time')
    filename = models.CharField(max_length=64, blank=True, verbose_name='Filename') #Set as unique filename, and uuid. see hashFilename.
    create_user = models.ForeignKey(User, verbose_name='Creator')

# get data in form.
def loadFromRequest(request):
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
    deploy_method = request.POST.get('deploy_method')
    deploy_url = request.POST.get('deploy_url')
    cowdir = request.POST.get('cowdir')
    create_user = request.user
    return {'name':name,'description':description,'capabilities':capabilities,'os_type':os_type,'distribution':distribution,'release':release,'kernel':kernel,'packages':packages,'repository':repository,'memory':memory,'disk':disk, 'newconfig':newconfig,'deploy_method':deploy_method,'deploy_url':deploy_url,'cowdir':cowdir,'create_user':create_user}

# use XML information and username to get hash code, used as the xml file name
def hashFilename(dict):
    dict_str = dict.copy()
    dict_str['create_user'] = dict['create_user'].username
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
        return new_tp
    except:
        return None
