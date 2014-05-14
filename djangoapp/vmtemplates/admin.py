from django.contrib import admin

# Register your models here.

from djangoapp.vmtemplates.models import VMTemplate

class VMTemplateAdmin(admin.ModelAdmin):
	list_display = ('name', 'os_type', 'distribution', 'deploy_method', 'create_user', 'create_time')
	search_fields = ('name','os_type', 'distribution', 'deploy_method', 'create_user__username')
	fields = ('name','os_type','distribution','deploy_method','kernel','node_type','capabilities','memory','disk','description','repository','deploy_url','create_user','filename')

admin.site.register(VMTemplate, VMTemplateAdmin)
