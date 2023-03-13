import openai
import os
import torch

from django.core.files.storage import default_storage
import whisper
from pydub import AudioSegment
from asgiref.sync import sync_to_async

from .models import MediaField

# openai.api_key = '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' # TODO Mine
# openai.api_key = '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' # TODO BOSS
openai.api_key = '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'  # TODO NEW ACCOUNT
model = whisper.load_model("base")


class Transcribe:

    @staticmethod
    def get_audio_file(file):
        path = default_storage.path(file.upload_file.name)
        if (file.upload_file.name.endswith('.mp4')):
            audio = AudioSegment.from_file(path, format='mp4')
            dir_path = os.path.dirname(path)
            new_file_name = file.upload_file.name.replace('.mp4', '.mp3')
            new_file_path = os.path.join(dir_path, new_file_name)
            audio.export(new_file_path, format='mp3')
            path = new_file_path
        return path

    def transcribe_file(self, file_id):
        file = MediaField.objects.filter(id=int(file_id)).first()

        filepath = os.path.join(f'media{file.upload_file.url}')
        # Note: you need to be using OpenAI Python v0.27.0 for the code below to work
        with open(filepath, "rb") as f:
            transcript = openai.Audio.transcribe("whisper-1", f)
            file.transcript = transcript['text']
            file.save()

    # def transcribe_file(self, file_id):
    #     file = MediaField.objects.filter(id=int(file_id)).first()
    #     if not file:
    #         return None

    #     # Get the path of the audio file
    #     audio_file = Transcribe.get_audio_file(file)

    #     # Transcribe the audio file
    #     transcription = model.transcribe(audio_file, fp16=torch.cuda.is_available(), language='urdu')

    #     # Update the transcript field of the MediaField object
    #     file.transcript = transcription['text'].strip()
    #     file.save()

    #     # Delete the audio file
    #     if os.path.exists(audio_file):
    #         os.remove(audio_file)

    #     return file
