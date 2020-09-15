from django.contrib import admin
from core.models import *


class EmployeeAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Employee._meta.fields]


admin.site.register(Employee, EmployeeAdmin)

admin.site.register(Company)

admin.site.register(Block)
admin.site.register(Header)
