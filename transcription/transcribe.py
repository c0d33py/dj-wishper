import os
from django.core.files.storage import default_storage
import whisper
from pydub import AudioSegment
from asgiref.sync import sync_to_async

from .models import MediaField

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
        if not file:
            return None

        # Get the path of the audio file
        audio_file = Transcribe.get_audio_file(file)

        # Transcribe the audio file
        transcription = model.transcribe(audio_file)

        # Update the transcript field of the MediaField object
        file.transcript = transcription['text'].strip()
        file.save()

        # Delete the audio file
        if os.path.exists(audio_file):
            os.remove(audio_file)

        return file
