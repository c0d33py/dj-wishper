from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import MediaField

from .tasks import get_transcript
# from .transcribe import Transcribe


@receiver(post_save, sender=MediaField)
def save_media_field(sender, instance, created, **kwargs):
    ''' Run Transcribe '''
    if created:
        get_transcript.delay(instance.id)
        # transcriber = Transcribe()  # Initialize
        # transcriber.transcribe_file(str(instance.id))
