from django.contrib import admin

# Register your models here.

from djangoapp.vmtemplates.models import VMTemplate

class VMTemplateAdmin(admin.ModelAdmin):
	list_display = ('name', 'os_type', 'distribution', 'deploy_method', 'create_user', 'create_time')
	search_fields = ('name','os_type', 'distribution', 'deploy_method', 'create_user__username')
	# fields = ('name','description','capabilities','os_type','kernel','distribution','release','kernel','packages','repository','repository','memory','disk','newconfig','deploy_method','deploy_url','cowdir','create_user','filename','create_time')

admin.site.register(VMTemplate, VMTemplateAdmin)

