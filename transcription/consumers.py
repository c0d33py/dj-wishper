'''
    This is the consumer that will be used to handle the websocket connection to the client and the
    transcription of the audio file.

    The consumer will be called by the websocket url in the urls.py file. The consumer will then
    call the transcribe_file method in the transcribe.py file to transcribe the audio file.
'''
import os
import json
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.shortcuts import get_object_or_404
from django.apps import apps

from faster_whisper import WhisperModel


class TranscriptConsumer(AsyncJsonWebsocketConsumer):

    def __init__(self):
        super().__init__()
        from .transcribe import Transcribe
        self.model_path = "model/whisper-large-v2-ct2-int8_float16/"
        self.transcribe = Transcribe()

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_node):
        await self.close()

    async def receive_json(self, content):

        try:
            file_id = content['file_id']
            transcription = content['transcription']
            cuda = content['cuda']
        except KeyError as e:
            await self.send(json.dumps({'alrt': f"Missing {e} key", 'type': 'danger'}))
            return

        if transcription:
            # Get cuda device if cuda is true and set the cuda device
            device = 'cuda' if cuda else 'cpu'
            model = WhisperModel(self.model_path, device=device, compute_type="int8")
            await self.send(json.dumps({'alrt': f"Using {device} device", 'type': 'info'}))

            # Get the model dynamically
            TusFileModel = await sync_to_async(apps.get_model)('django_tus', 'TusFileModel')
            tus_file = await sync_to_async(get_object_or_404)(TusFileModel, guid=file_id)

            if tus_file is None:
                return None

            # Convert the audio file to a mono WAV audio file
            audio_data = await sync_to_async(self.transcribe.get_audio_file)(tus_file.uploaded_file.name)
            segments, info = model.transcribe(audio_data, beam_size=5)

            # Send the transcription to the client
            paragraph = ""
            for segment in segments:
                paragraph += segment.text + " "

            await self.send(json.dumps({
                'transcript': paragraph,
                'alrt': 'Transcription complete',
                'type': 'success'
            }))

            # Update the TusFileModel object to reference the MediaField object
            MediaField = await sync_to_async(apps.get_model)('transcription', 'MediaField')
            transcribe_instance = await sync_to_async(MediaField.objects.create)(transcript=paragraph)
            tus_file.content_object = transcribe_instance
            await sync_to_async(tus_file.save)()

            # Delete the temporary audio file
            await sync_to_async(os.remove)(audio_data)

            # Close the connection
            await self.close()
        else:
            await self.send(json.dumps({'alrt': 'Transcription is disabled', 'type': 'warning'}))
            await self.close()
