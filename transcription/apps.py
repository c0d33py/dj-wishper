from django.apps import AppConfig


class TranscriptionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transcription'

    def ready(self):
        '''Implicitly connect signal handlers decorated with @receiver.'''
        # from . import signals
