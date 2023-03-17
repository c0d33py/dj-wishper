# import openai
import os
import whisper
import torch
from functools import lru_cache

from django.core.files.storage import default_storage

from .models import MediaField


@lru_cache()
def transcribe_audio(audio_file_path):
    model = whisper.load_model('large')

    # Transcribe the audio file using the loaded model
    transcription = model.transcribe(
        audio_file_path,
        fp16=torch.cuda.is_available(),
        language='urdu'
    )

    return transcription['text'].strip()


class Transcribe:

    @staticmethod
    def get_audio_file(file):
        path = default_storage.path(file.upload_file.name)
        # Create a new file name
        new_file_name = path.replace('.mp4', '.wav')

        # Convert the file
        os.system(f'ffmpeg -y -i {path} {new_file_name}')

        return new_file_name

    def transcribe_file(self, file_id):
        file = MediaField.objects.filter(id=int(file_id)).first()
        if not file:
            return None

        # Get the path of the audio file
        audio_file = Transcribe.get_audio_file(file)

        transcription = transcribe_audio(audio_file)

        file.transcript = transcription
        file.save()
        os.remove(audio_file)

        return audio_file

    # def transcribe_files(self, file_id):
    #     model = whisper.load_model('large')
    #     torch = lazy_imports('torch')

    #     file = MediaField.objects.filter(id=int(file_id)).first()
    #     if not file:
    #         return None

    #     # Get the path of the audio file
    #     audio_file = Transcribe.get_audio_file(file)

    #     # Transcribe the audio file
    #     transcription = model.transcribe(
    #         audio_file,
    #         fp16=torch.cuda.is_available(),
    #         language='urdu'
    #     )

    #     # Update the transcript field of the MediaField object
    #     file.transcript = transcription['text'].strip()
    #     file.save()

    #     # Delete the audio file
    #     os.remove(audio_file)

    #     return file

    # def transcribe_file(self, file_id):
    #     file = MediaField.objects.filter(id=int(file_id)).first()

    #     filepath = os.path.join(f'media{file.upload_file.url}')
    #     # Note: you need to be using OpenAI Python v0.27.0 for the code below to work
    #     with open(filepath, "rb") as f:
    #         transcript = openai.Audio.transcribe("whisper-1", f)
    #         file.transcript = transcript['text']
    #         file.save()
