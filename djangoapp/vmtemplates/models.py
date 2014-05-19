from django.db import models
from djangoapp.settings import *
import datetime
from django.contrib.auth.models import User
import os

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
    cpu = models.IntegerField(verbose_name='vCPU(Only Int)',default=1)
    # Method
    deploy_method = models.CharField(max_length=30, default='nfsmount', verbose_name='Deploy Method')
    # URL
    deploy_url = models.CharField(max_length=200, verbose_name='Deploy URL')
    # COWDir
    cowdir = models.CharField(max_length=200, verbose_name='COWDir')

# Not In XML
    create_time = models.DateTimeField(default = datetime.datetime.now, verbose_name='Created Time')
    filename = models.CharField(max_length=64, blank=True, verbose_name='Filename') #Set as unique filename, and uuid. see hashFilename.
    create_user = models.ForeignKey(User, verbose_name='Creator')
    status = models.IntegerField(default = 0)#0: created, 1:transfer, 2:publish, 3:ready, -1:error

    def dumps(self):
        content = "<?xml version=\"1.0\" ?>\n"
        content += "<vTemplate uuid=\"" + self.filename +"\">\n"
        content += " <Name>\n  " + self.name + "\n </Name>\n"
        content += " <Description>\n  " + self.description + "\n </Description>\n"
        content += " <Capabilities>\n  " + self.capabilities + "\n </Capabilities>\n"
        content += " <OS>\n"
        content += "  <Type>\n   " + self.os_type + "\n  </Type>\n"
        content += "  <Distribution>\n   " + self.distribution + "\n  </Distribution>\n"
        content += "  <Release>\n   " + self.release + "\n  </Release>\n"
        content += "  <Kernel>\n   "  + self.kernel + "\n  </Kernel>\n"
        content += "  <Packages>\n   " + self.packages + "\n  </Packages>\n"
        content += " </OS>\n"
        content += " <Repository>\n  " + self.repository + "\n </Repository>\n"
        content += " <DeployInfo>\n"
        content += "  <PreferedSettings>\n"
        content += "   <vCPU>\n     " + str(self.cpu) + "\n    </vCPU>\n"
        content += "   <Mem>\n    " + str(self.memory) + "\n   </Mem>\n"
        content += "   <DiskSize>\n    " + str(self.disk) + "G\n   </DiskSize>\n"
        content += "  </PreferedSettings>\n"
        content += "  <Method>\n   " + self.deploy_method + "\n  </Method>\n"
        content += "  <URL>\n   " + self.deploy_url + "\n  </URL>\n"
        content += "  <COWDir>\n   " + self.cowdir + "\n  </COWDir>\n"
        content += " </DeployInfo>\n"
        content += "</vTemplate>"
        filepath = os.path.join(LOCAL_XML_DIR, self.filename + '.xml')
        fileobj = open(filepath,'w')
        fileobj.write(content)
        fileobj.close()
        return content


