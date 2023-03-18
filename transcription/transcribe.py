import os
import subprocess

from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from django_tus.models import TusFileModel

from .model_loader import ModelLoader
from .models import MediaField


class Transcribe:

    @staticmethod
    def get_audio_file(file):
        """
        Converts the uploaded video file to a mono WAV audio file using FFmpeg.

        Args:
            file (django.core.files.File): The uploaded video file.

        Returns:
            The path to the converted audio file.
        """
        # Set up the input and output paths
        input_path = default_storage.path(file)
        output_path = input_path.replace('.mp4', '.wav')

        # Build the FFmpeg command as a list of arguments
        ffmpeg_cmd = [
            'ffmpeg',
            '-y',  # Overwrite output files without asking
            '-i', input_path,
            '-vn',  # Disable video recording
            '-ac', '1',  # Set audio channels to 1 (mono)
            '-ar', '44100',  # Set audio sample rate to 44.1kHz
            '-acodec', 'pcm_s16le',  # Set audio codec to PCM 16-bit
            output_path,
        ]

        # Execute the FFmpeg command using subprocess.run()
        subprocess.run(ffmpeg_cmd, capture_output=True, check=True)

        return output_path

    def transcribe_file(self, file_id: int) -> TusFileModel:
        """
        Transcribes the audio file identified by the given `file_id` using a pre-trained model,
        and updates the transcript field of the corresponding `MediaField` object.

        Args:
            file_id (int): The ID of the `TusFileModel` object representing the audio file.

        Returns:
            The `TusFileModel` object corresponding to the transcribed audio file.
            None if the `TusFileModel` object does not exist.
        """
        # Get the TusFileModel object corresponding to the given file_id
        tus_file = get_object_or_404(TusFileModel.objects.only('guid'), guid=file_id)

        if tus_file is None:
            return None

        # Convert the audio file to a mono WAV audio file
        audio_data = Transcribe.get_audio_file(tus_file.uploaded_file.name)

        # Load the pre-trained transcription model
        model = ModelLoader().get_model()

        # Transcribe the audio file using the model
        transcription = model.transcribe(audio_data, language='urdu')

        # Create a new MediaField object for the transcribed text
        transcribe_instance = MediaField.objects.create(transcript=transcription['text'].strip())

        # Update the TusFileModel object to reference the MediaField object
        tus_file.content_object = transcribe_instance
        tus_file.save()

        # Delete the temporary audio file
        os.remove(audio_data)

        # Return the TusFileModel object
        return tus_file
