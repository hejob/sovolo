from django.contrib import admin
from .models import Policy

class PolicyAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'html', 'modified', 'is_active')

admin.site.register(Policy, PolicyAdmin)
