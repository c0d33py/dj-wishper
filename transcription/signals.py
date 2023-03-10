from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import MediaField
from .transcribe import Transcribe


@receiver(post_save, sender=MediaField)
def save_media_field(sender, instance, created, **kwargs):
    if created:
        ''' Run Transcribe '''
        Transcribe.transcribe_file(instance.id)
