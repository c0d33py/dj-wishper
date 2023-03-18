# from django.db.models.signals import post_save
from django.dispatch import receiver

from django_tus.signals import tus_upload_finished_signal

# from .tasks import get_transcript
from .transcribe import Transcribe


@receiver(tus_upload_finished_signal)
def create_file(sender, **kwargs):
    ''' 
    Called when Django-Tus signals 
    that a file has been uploaded 
    '''
    resource_id = kwargs.get('resource_id')
    # get_transcript.delay(instance.id)
    Transcribe().transcribe_file(resource_id)


# @receiver(post_save, sender=MediaField)
# def save_media_field(sender, instance, created, **kwargs):
#     ''' Transcribe Signal '''
#     if created:
#         # get_transcript.delay(instance.id)
#         transcriber = Transcribe()  # Initialize
#         transcriber.transcribe_file(str(instance.id))
