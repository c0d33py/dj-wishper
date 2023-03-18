from datetime import datetime

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models


def unique_filename(_, filename):
    name, ext = filename.split('.')
    filename = f'{name}.{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.{ext}'
    return filename


class MediaField(models.Model):

    upload_file = GenericRelation('django_tus.TusFileModel', related_query_name='media_field')
    transcript = models.TextField()

    class Meta:
        verbose_name = 'media file'
        verbose_name_plural = 'media files'
        ordering = ['-id']

    def __str__(self):
        return str(self.id)
