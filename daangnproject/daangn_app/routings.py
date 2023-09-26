# routing.py

from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from daangn_app import consumers

application = ProtocolTypeRouter({
    "websocket": URLRouter([
        re_path(r'ws/chat/(?P<chat_room_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    ]),
})
