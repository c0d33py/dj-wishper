'''
    This is the consumer that will be used to handle the websocket connection to the client and the
    transcription of the audio file.

    The consumer will be called by the websocket url in the urls.py file. The consumer will then
    call the transcribe_file method in the transcribe.py file to transcribe the audio file.
'''

from channels.generic.websocket import AsyncJsonWebsocketConsumer, AsyncWebsocketConsumer


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

        file_id = content['file']
        # data = await self.transcribe.transcribe_file(file_id)
        return await self.send_json({'type': 'TRANSFORM', 'value': 'data'})
