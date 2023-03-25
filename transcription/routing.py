'''
This file is used to define the routing for the websocket connection.

The routing is defined in the wesocket_routing variable.

The wesocket_routing variable is a list of path objects.

The path object takes two arguments:
    1. The path to the websocket connection.
    2. The consumer that will handle the websocket connection.
'''

from django.urls import path
from transcription.consumers import TranscriptConsumer

wesocket_routing = [
    path('ws/transcript/', TranscriptConsumer.as_asgi()),
]
