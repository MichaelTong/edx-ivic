from django.db import models
from django.contrib.auth.models import User
import datetime

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
