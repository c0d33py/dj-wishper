import os
import subprocess

from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from django_tus.models import TusFileModel

from whisper import load_audio, pad_or_trim, log_mel_spectrogram, DecodingOptions, decode, load_model

from .model_loader import ModelLoader
from .models import MediaField
from faster_whisper import WhisperModel


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
        output_path = input_path.replace('.mp4', '.wav').replace('.mp3', '.wav')

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
        print("Loading file convert...")

        # Load the pre-trained transcription model
        # model = load_model('tiny')

        # # Run on GPU with FP16
        # # model = WhisperModel(model_path, device="cuda", compute_type="float16")
        model = ModelLoader().get_model()

        print("Transcribing audio file...")

        segments, info = model.transcribe(audio_data, beam_size=5)

        paragraph = ""

        for segment in segments:
            paragraph += segment.text + " "

        # Create a new MediaField object for the transcribed text
        transcribe_instance = MediaField.objects.create(transcript=paragraph)

        # # Update the TusFileModel object to reference the MediaField object
        tus_file.content_object = transcribe_instance
        tus_file.save()

        # print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

        # segments = sorted(segments, key=lambda s: s.start)

        # print("Transcription:", segments[0].text)

        # for segment in segments:
        #     print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

        ############################################################

        # Transcribe the audio file using the model and return the result # TODO: Not in use yet
        # transcription = model.transcribe(audio_data, language='urdu')

        # load audio and pad/trim it to fit 30 seconds
        # audio = load_audio(audio_data)
        # trim_audio = pad_or_trim(audio)

        # # make log-Mel spectrogram and move to the same device as the model
        # mel = log_mel_spectrogram(trim_audio).float().to(model.device)

        # # detect the spoken language
        # _, probs = model.detect_language(mel)
        # print(f"Detected language: {max(probs, key=probs.get)}")

        # # decode the audio
        # options = DecodingOptions()
        # transcription = decode(model, mel, options)
        # print(transcription.text)

        # Create a new MediaField object for the transcribed text
        # transcribe_instance = MediaField.objects.create(transcript=transcription['text'].strip())

        # # Update the TusFileModel object to reference the MediaField object
        # tus_file.content_object = transcribe_instance
        # tus_file.save()

        # Delete the temporary audio file
        os.remove(audio_data)

        # Return the TusFileModel object
        return tus_file

# load audio and pad/trim it to fit 30 seconds
# audio = whisper.load_audio("audio.mp3")
# audio = whisper.pad_or_trim(audio)

# # make log-Mel spectrogram and move to the same device as the model
# mel = whisper.log_mel_spectrogram(audio).to(model.device)

# # detect the spoken language
# _, probs = model.detect_language(mel)
# print(f"Detected language: {max(probs, key=probs.get)}")

# # decode the audio
# options = whisper.DecodingOptions()
# result = whisper.decode(model, mel, options)
