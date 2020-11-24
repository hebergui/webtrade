from django.contrib import admin
from .models import *


class EmployeeAdmin(admin.ModelAdmin):
    # TODO: correct this warning
    list_display = [f.name for f in Employee._meta.fields]


admin.site.register(Employee, EmployeeAdmin)

admin.site.register(Company)
admin.site.register(Indicator)
