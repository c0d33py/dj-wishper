from django.db import models


class MediaField(models.Model):

    upload_file = models.FileField(upload_to='upload/')
    transcript = models.TextField()

    class Meta:
        verbose_name = 'media file'
        verbose_name_plural = 'media files'
        ordering = ['-id']

    def __str__(self):
        return self.upload_file
