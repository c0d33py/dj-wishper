'''
    This is the consumer that will be used to handle the websocket connection to the client and the
    transcription of the audio file.

    The consumer will be called by the websocket url in the urls.py file. The consumer will then
    call the transcribe_file method in the transcribe.py file to transcribe the audio file.
'''
import asyncio
import os
import json
import time
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer, AsyncWebsocketConsumer
from django.shortcuts import get_object_or_404
from django.apps import apps

from faster_whisper import WhisperModel


class TranscriptConsumer(AsyncWebsocketConsumer):

    def __init__(self):
        super().__init__()
        from .transcribe import Transcribe
        self.model_path = "model/whisper-large-v2-ct2-int8_float16/"
        self.transcribe = Transcribe()

    # async def send_transcripts(self, text_data):

    async def receive(self, text_data):
        # Parse the JSON-encoded text_data into a Python dictionary
        try:
            data = json.loads(text_data)
            file_id = data['file_id']
            transcription = data['transcription']
            cuda = data['cuda']
        except (KeyError, json.JSONDecodeError):
            await self.send(json.dumps({'alrt': 'Invalid message received', 'type': 'danger'}))
            return

        if transcription:
            # Get cuda device if cuda is true and set the cuda device
            DEVICE = 'cuda' if cuda else 'cpu'
            model = WhisperModel(self.model_path, device=DEVICE, compute_type="int8")
            await self.send(json.dumps({'alrt': f"Using {DEVICE} device", 'type': 'info'}))

            # Get the model dynamically
            TusFileModel = await sync_to_async(apps.get_model)('django_tus', 'TusFileModel')
            tus_file = await sync_to_async(get_object_or_404)(TusFileModel, guid=file_id)

            if tus_file is None:
                return None
            # Update the TusFileModel object to reference the MediaField object
            # MediaField = await sync_to_async(apps.get_model)('transcription', 'MediaField')
            # transcribe_instance = await sync_to_async(MediaField.objects.create)()
            # tus_file.content_object = transcribe_instance
            # await sync_to_async(tus_file.save)()

            # Convert the audio file to a mono WAV audio file
            # audio_data = await sync_to_async(self.transcribe.get_audio_file)(tus_file.uploaded_file.name)
            # segments, info = model.transcribe(audio_data, beam_size=5)

            # # # Send the transcription to the client
            # response = ''
            # for segment in segments:
            #     response += segment.text + ' '

            await self.send(json.dumps({
                'id': 45455,
                'transcript': 'So I am far may contented to find it on to The word so they know Charlie said the general what sir just then asked the chubby',
                'alrt': 'Transcription complete',
                'type': 'success'
            }))

            # transcribe_instance.transcript = response
            # await sync_to_async(transcribe_instance.save)()

            # Delete the temporary audio file
            # await sync_to_async(os.remove)(audio_data)
            await self.close()
        else:
            await self.send(json.dumps({'alrt': 'Transcription cancelled', 'type': 'info'}))
            await self.close()
