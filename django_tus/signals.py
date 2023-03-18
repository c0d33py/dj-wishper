import os
import django.dispatch
from django.dispatch import receiver

from .models import TusFileModel

tus_upload_finished_signal = django.dispatch.Signal()
"""
This signal provides the following keyword arguments:
    metadata
    filename
    upload_file_path
    file_size
    upload_url
    destination_folder
"""
