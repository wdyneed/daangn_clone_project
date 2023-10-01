import json

from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatMessage, chatroom, User
from django.utils import timezone
from asgiref.sync import sync_to_async
from .views import create_chat_message



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    
    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        is_sent_by_me = self.scope["user"].id
        w_n = User.objects.get(id=is_sent_by_me)
        room_name = int(self.room_name)
        r_n = chatroom.objects.get(id=room_name)
        curtime = timezone.now()
        
        create_chat_message(w_n, message, r_n, curtime)
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message, "isSentByMe": is_sent_by_me}
        )
        

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        is_sent_by_me = event["isSentByMe"]
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message, "isSentByMe": is_sent_by_me}))