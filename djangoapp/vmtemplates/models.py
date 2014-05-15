from django.db import models
from django.contrib.auth.models import User
import datetime
import hashlib
class VMTemplate(models.Model):
    kernel = models.CharField(max_length=30, blank=True, verbose_name='Kernel')
    deploy_method = models.CharField(max_length=30, default='nfsmount', verbose_name='Deploy Method')
    description = models.CharField(max_length=50, blank=True, verbose_name='Description')
    repository = models.CharField(max_length=100, blank=True, verbose_name='Repository')
    node_type = models.CharField(max_length=30, default='undefined', verbose_name='Node Type')
    deploy_url = models.CharField(max_length=200, verbose_name='Deploy URL')
    distribution = models.CharField(max_length=30, blank=True, verbose_name='Distribution')
    name = models.CharField(max_length=30, verbose_name='Name')
    capabilities = models.CharField(max_length=30, default='vNode', verbose_name='Capabilities')
    os_type = models.CharField(max_length=30, verbose_name='OS Type')
    memory = models.IntegerField(verbose_name='Perferred Memory(MB, Only Int)')
    disk = models.IntegerField(verbose_name='Perferred Disk Size(GB, Only Int)')
    create_time = models.DateTimeField(default = datetime.datetime.now, verbose_name='Created Time')
    filename = models.CharField(max_length=64, blank=True, verbose_name='Filename')
    create_user = models.ForeignKey(User, verbose_name='Creator')

def loadFromRequest(request):
    name = request.POST.get('name')
    os_type = request.POST.get('os_type')
    distribution = request.POST.get('distribution')
    deploy_method = request.POST.get('deploy_method')
    kernel = request.POST.get('kernel')
    node_type = request.POST.get('node_type')
    capabilities = request.POST.get('capabilities')
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
    repository = request.POST.get('repository')
    deploy_url = request.POST.get('deploy_url')
    description = request.POST.get('description')
    create_user = request.user
    return {'name':name,'os_type':os_type,'distribution':distribution,'deploy_method':deploy_method,'kernel':kernel,'node_type':node_type,'capabilities':capabilities,'memory':memory,'disk':disk,'repository':repository,'deploy_url':deploy_url,'description':description,'create_user':create_user}

def hashFilename(dict):
    dict_str = dict.copy()
    dict_str['create_user'] = dict['create_user'].username
    obj = hashlib.md5()
    obj.update(str(dict_str))
    hash = obj.hexdigest()
    filename = hash[0:8]+'-'+hash[8:12]+'-'+hash[12:16]+'-'+hash[16:20]+'-'+hash[20:32]
    return filename

def createNew(dict, filename):
    try:
        t = VMTemplate.objects.get(filename = filename)
        if t is not None:
            return t
    except:
        new_tp = VMTemplate.objects.create(name = dict['name'], os_type = dict['os_type'], distribution = dict['distribution'], deploy_method = dict['deploy_method'], kernel = dict['kernel'], node_type = dict['node_type'], capabilities = dict['capabilities'], memory = dict['memory'], disk = dict['disk'], repository = dict['repository'], deploy_url = dict['deploy_url'], description = dict['description'], create_user = dict['create_user'],filename = filename)
        return new_tp
