'''
    This is the consumer that will be used to handle the websocket connection to the client and the
    transcription of the audio file.

    The consumer will be called by the websocket url in the urls.py file. The consumer will then
    call the transcribe_file method in the transcribe.py file to transcribe the audio file.
'''

import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.shortcuts import get_object_or_404
from django.apps import apps


from transcription.model_loader import ModelLoader


class TranscriptConsumer(AsyncJsonWebsocketConsumer):

    def __init__(self):
        super().__init__()
        from .transcribe import Transcribe
        self.transcribe = Transcribe()

    async def connect(self):
        print('connected')
        await self.accept()

    async def disconnect(self, close_node):
        print('disconnected')
        await self.close()

    async def receive_json(self, content):
        file_id = content['file_id']

        # Get the model dynamically
        # TusFileModel = await sync_to_async(apps.get_model)('django_tus', 'TusFileModel')

        # # Get the TusFileModel object corresponding to the given file_id
        # tus_file = await sync_to_async(get_object_or_404)(TusFileModel, pk=file_id)

        # if tus_file is None:
        #     return None

        # # Convert the audio file to a mono WAV audio file
        # audio_data = await sync_to_async(self.transcribe.get_audio_file)(tus_file.uploaded_file.name)

        # # Load the pre-trained transcription model
        # model = await sync_to_async(ModelLoader().get_model)()

        # # Transcribe the audio file
        # segments, info = model.transcribe(audio_data, beam_size=5)

        # # Send the transcription to the client
        # for segment in segments:
        await self.send(
            json.dumps({'transcript': 'The word so they know Charlie said the general what sir just then asked the chubby'})
        )
