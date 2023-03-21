# channel route for websocket
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from transcription.consumers import TranscriptConsumer

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path('ws/transcript/', TranscriptConsumer.as_asgi()),
        ])
    )
})
