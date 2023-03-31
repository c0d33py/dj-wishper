'''
    This is the consumer that will be used to handle the websocket connection to the client and the
    transcription of the audio file.

    The consumer will be called by the websocket url in the urls.py file. The consumer will then
    call the transcribe_file method in the transcribe.py file to transcribe the audio file.
'''
import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class TranscriptConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        await self.close()

    # Receive message from WebSocket
    async def receive(self, text_data):
        # Send message to room group
        await self.send(text_data=json.dumps({
            'message': text_data
        }))
