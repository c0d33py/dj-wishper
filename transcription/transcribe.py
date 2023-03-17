# import openai
import os
import subprocess

from django.core.files.storage import default_storage

from .model_loader import ModelLoader
from .models import MediaField


class Transcribe:

    @staticmethod
    def get_audio_file(file):
        input_path = default_storage.path(file.upload_file.name)
        # Create a new file name
        output_path = input_path.replace('.mp4', '.wav')

        # Build the command as a list of arguments
        command = [
            'ffmpeg',
            '-y',  # Overwrite output files without asking
            '-i', input_path,
            '-vn',  # Disable video recording
            '-ac', '1',  # Set audio channels to 1 (mono)
            '-ar', '44100',  # Set audio sample rate to 44.1kHz
            '-acodec', 'pcm_s16le',  # Set audio codec to PCM 16-bit
            output_path,
        ]

        # Use subprocess.run() to execute the command
        subprocess.run(command, capture_output=True)

        return output_path

    def transcribe_file(self, file_id):

        # Get the MediaField object
        file = MediaField.objects.filter(id=int(file_id)).first()
        if not file:
            return None

        # Get the path of the audio file
        audio_data = Transcribe.get_audio_file(file)

        # Load the large model
        model = ModelLoader().get_model()

        # Transcribe the audio file
        transcription = model.transcribe(audio_data, language='urdu')

        # Update the transcript field of the MediaField object
        file.transcript = transcription['text'].strip()
        file.save()

        # Delete the audio file
        os.remove(audio_data)

        return file

    # def transcribe_file(self, file_id):
    #     file = MediaField.objects.filter(id=int(file_id)).first()

    #     filepath = os.path.join(f'media{file.upload_file.url}')
    #     # Note: you need to be using OpenAI Python v0.27.0 for the code below to work
    #     with open(filepath, "rb") as f:
    #         transcript = openai.Audio.transcribe("whisper-1", f)
    #         file.transcript = transcript['text']
    #         file.save()
