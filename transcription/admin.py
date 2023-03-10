from django.contrib import admin

from .models import MediaField


@admin.register(MediaField)
class MediaFieldAdmin(admin.ModelAdmin):
    list_display = ['id', 'upload_file']
