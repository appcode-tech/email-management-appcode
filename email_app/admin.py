from django.contrib import admin
from . models import *

# Register your models here.

@admin.register(EmailLogsMaster)
class EmailLogsMasterAdmin(admin.ModelAdmin):
    list_display = [f.name for f in EmailLogsMaster._meta.fields]

@admin.register(EmailAttachments)
class EmailAttachmentsAdmin(admin.ModelAdmin):
    list_display = [f.name for f in EmailAttachments._meta.fields]