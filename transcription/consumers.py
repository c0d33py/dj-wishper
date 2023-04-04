import os
import asyncio
import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from faster_whisper import WhisperModel

from django.apps import apps
from django.shortcuts import get_object_or_404


class TranscriptConsumer(AsyncWebsocketConsumer):
    """
    This is a consumer that will be used to handle the WebSocket connection to the client and the transcription of the
    audio file.

    Attributes:
        model (str): The path to the model directory.
        transcribe (Transcribe): The `Transcribe` instance.
        stream (WhisperModel): The `WhisperModel` instance.
        tus_file (TusFileModel): The `TusFileModel` instance.

    Methods:
        connect(self)
            Accepts the WebSocket connection.

        disconnect(self, close_code)
            Stops the WebSocket connection.

        receive_audio(self, file_id)
            Gets the `TusFileModel` object and retrieves the audio data.

        receive(self, text_data)
            Receives the WebSocket message and processes the transcription.

        media_prepared(self)
            Creates a `MediaField` instance and associates it with the `TusFileModel` object.

        process_transcription(self, segments)
            Processes the transcription results and sends them back to the client.
    """

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
            # self.stream.transcribe(audio_data, beam_size=5)
            segments, info = await sync_to_async(self.stream.transcribe)(audio_data, beam_size=5)
            # Process the transcription results
            await self.process_transcription(segments, info.language, info.language_probability)
            # Delete the temporary audio file
            await sync_to_async(os.remove)(audio_data)
            # Close the WebSocket connection
            await self.disconnect(1000)

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

    async def process_transcription(self, segments, language, language_probability):
        # Get the media instance
        instance = await self.media_prepared()
        # Send transcription results back to client
        paragraph = ''
        for segment in segments:
            paragraph += segment.text + ' '
            await asyncio.sleep(1)  # Sleep for 1 second
            await self.send(json.dumps({
                'id': instance.id,
                'transcript': segment.text,
                'language': language,
                'language_probability': language_probability,
                'alrt': 'Transcription complete',
                'type': 'success'
            }))
        # Save the transcription instance
        instance.transcript = paragraph
        instance.language = language
        instance.language_probability = language_probability
        await sync_to_async(instance.save)()

    # async def test_func(self):
    #     try:
    #         text = "So I am far may contented to find it on to The word so they know Charlie said the general what sir just then asked the chubby"

    #         words = text.split()

    #         for i in range(0, len(words), 4):
    #             group = " ".join(words[i:i + 4])
    #             await asyncio.sleep(1)  # Sleep for 1 second
    #             await self.send(json.dumps({
    #                 'id': 45455,
    #                 'transcript': group,
    #                 'alrt': 'Transcription complete',
    #                 'type': 'success'
    #             }))
    #     except Exception as e:
    #         print(e)
