'''
    This is the consumer that will be used to handle the websocket connection to the client and the
    transcription of the audio file.

    The consumer will be called by the websocket url in the urls.py file. The consumer will then
    call the transcribe_file method in the transcribe.py file to transcribe the audio file.
'''
import os
import asyncio
import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from faster_whisper import WhisperModel

from django.apps import apps
from django.shortcuts import get_object_or_404


class TranscriptConsumer(AsyncWebsocketConsumer):

    def __init__(self):
        super().__init__()
        from .transcribe import Transcribe
        self.model = "model/whisper-large-v2-ct2-int8_float16/"
        self.transcribe = Transcribe()
        self.stream = None
        self.tus_file = None

    async def connect(self):
        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Stop the WebSocket connection
        await self.close()

    async def receive_audio(self, file_id):
        # Get the model dynamically & Convert the audio file to a mono WAV audio file
        TusFileModel = await sync_to_async(apps.get_model)('django_tus', 'TusFileModel')
        # Get the TusFileModel object
        self.tus_file = await sync_to_async(get_object_or_404)(TusFileModel, guid=file_id)
        # Get the audio data
        audio_data = await sync_to_async(self.transcribe.get_audio_file)(self.tus_file.uploaded_file.name)
        return audio_data

    async def receive(self, text_data):
        # Parse the JSON-encoded text_data into a Python dictionary
        try:
            data = json.loads(text_data)
            file_id = data['file_id']
            transcription = data['transcription']
            cuda = data['cuda']
        except (KeyError, json.JSONDecodeError):
            await self.send(json.dumps({'alrt': 'Invalid message received', 'type': 'danger'}))

        if transcription:
            # Get cuda device if cuda is true and set the cuda device
            DEVICE = 'cuda' if cuda else 'cpu'
            await self.send(json.dumps({'device': DEVICE}))
            # Create a Whisper model instance
            self.stream = WhisperModel(self.model, device=DEVICE, compute_type="int8")
            # Get audio data from message
            audio_data = await self.receive_audio(file_id)
            # # Process audio data with Whisper
            segments, info = self.stream.transcribe(audio_data, beam_size=5)
            # Process the transcription results
            await self.process_transcription(segments)
            # Delete the temporary audio file
            await sync_to_async(os.remove)(audio_data)

    async def media_prepared(self):
        # Get the model dynamically
        MediaField = await sync_to_async(apps.get_model)('transcription', 'MediaField')
        # Create a media instance
        media_instance = await sync_to_async(MediaField.objects.create)()
        # Associate the TusUpload object with the media instance
        self.tus_file.content_object = media_instance
        # Save the TusUpload object
        await sync_to_async(self.tus_file.save)()
        return media_instance

    async def process_transcription(self, segments):
        # Get the media instance
        instance = await self.media_prepared()
        # Send transcription results back to client
        paragraph = ''
        for segment in segments:
            paragraph += segment.text + ' '
            await asyncio.sleep(1)  # Sleep for 1 second
            await self.send(json.dumps({
                'id': instance.id,
                'text': segment.text,
                'alrt': 'Transcription complete',
                'type': 'success'
            }))

        # Save the transcription instance
        instance.transcript = paragraph
        await sync_to_async(instance.save)()
