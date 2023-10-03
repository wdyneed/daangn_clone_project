import json

from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatMessage, chatroom, User, DisconnectInfo
from django.utils import timezone
from asgiref.sync import sync_to_async
from .views import create_chat_message, change_chatroom_time
from datetime import datetime


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
        await self.save_disconnect_info()
        
    async def save_disconnect_info(self):
        user_id = self.scope["user"].id
        chat_room_id = self.room_name
        disconnect_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        disconnect_info = DisconnectInfo.objects.filter(user_id=user_id, chat_room_id=chat_room_id).first()
       
        if disconnect_info:
            disconnect_info.disconnect_time = disconnect_time
            disconnect_info.save()
            
        else:
            disconnect_info = DisconnectInfo(user_id=user_id, chat_room_id=chat_room_id, disconnect_time=disconnect_time)
            disconnect_info.save()
    
        # 여기서 disconnect 정보를 저장하는 로직을 추가합니다.
        # 예를 들어, DisconnectInfo 모델을 사용하여 정보를 저장할 수 있습니다.
        
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
        change_chatroom_time(room_name)
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