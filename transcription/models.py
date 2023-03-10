from datetime import datetime
from django.core.validators import FileExtensionValidator
from django.db import models


def unique_filename(_, filename):
    name, ext = filename.split('.')
    filename = f'{name}.{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.{ext}'
    return filename


class MediaField(models.Model):

    upload_file = models.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['mp3', 'mp4'])],
        upload_to=unique_filename
    )
    transcript = models.TextField()

    class Meta:
        verbose_name = 'media file'
        verbose_name_plural = 'media files'
        ordering = ['-id']

    def __str__(self):
        return self.upload_file
