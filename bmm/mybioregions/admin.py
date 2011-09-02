from django.contrib import admin

from django.contrib.auth.models import Permission
admin.site.register(Permission)

from models import MyBioregion, Folder

class MyBioregionAdmin(admin.ModelAdmin):
    list_display = ( 'pk', 'name', 'user', 'date_created', 'date_modified')
    list_filter = ['date_modified','date_created']
    search_fields = ('name','id','user__username','user__first_name','user__last_name')
    
admin.site.register(MyBioregion, MyBioregionAdmin)

class FolderAdmin(admin.ModelAdmin):
    list_display = ( 'pk', 'name', 'user', 'date_created', 'date_modified')
    list_filter = ['date_modified','date_created']
    search_fields = ('name','id','user__username','user__first_name','user__last_name')
    
admin.site.register(Folder, FolderAdmin)

