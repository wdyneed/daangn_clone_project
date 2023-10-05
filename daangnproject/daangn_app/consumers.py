import json

from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatMessage, chatroom, User, DisconnectInfo, ai_chatroom
from django.utils import timezone
from asgiref.sync import async_to_sync
from .views import create_chat_message, change_chatroom_time, create_aichat_message
from datetime import datetime
from django.conf import settings
import requests, aiohttp, asyncio

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
        

# AI 챗봇용 웹소켓
class AIChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_room = self.scope['url_route']['kwargs']['user_room']
        self.room_group_name = f"ai_chat_{self.user_room}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    async def chat_message(self, event):
        message = event['message']
        is_sent_by_me = event["isSentByMe"]
        await self.send(text_data=json.dumps({"message": message, "isSentByMe": is_sent_by_me}))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        is_sent_by_me = self.scope["user"].id
        w_n = User.objects.get(id=is_sent_by_me)
        user_room = int(self.user_room)
        r_n = ai_chatroom.objects.get(id=user_room)
        curtime = timezone.now()
        
        create_aichat_message(w_n.id, message, r_n, curtime)

        await self.send(
        text_data=json.dumps({"message": message, "isSentByMe": is_sent_by_me}) 
        )
        # ChatGPT 응답을 받아옴
        gpt_response = await self.get_chatgpt_response(message)

        create_aichat_message(9999, gpt_response, r_n, curtime)
        # ChatGPT의 응답을 클라이언트에게 보내기
        await self.send(text_data=json.dumps({
            'message': gpt_response,
            'isSentByMe': False,  # 챗봇이 보낸 메시지라고 표시
        }))
            
    async def get_chatgpt_response(self, message):
        # ChatGPT API 호출
        api_url = 'https://api.openai.com/v1/chat/completions'
        api_key = settings.API_KEY

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        messages = [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': message},
        ]
        data = {
            "model": "gpt-3.5-turbo",
            'messages': messages,
            'max_tokens': 500,
            'temperature': 0.5,
        }
        response_data, response_status = await self.send_chatgpt_api_request(api_url, headers, data)

        if response_status == 200:
            if 'choices' in response_data and response_data['choices']:
                response_text = response_data['choices'][0].get('message', {}).get('content')
                if response_text:
                    return response_text
                else:
                    return 'No response from ChatGPT'
            else:
                return 'No response from ChatGPT'
        else:
            return f'ChatGPT API 호출 오류 (HTTP 상태 코드: {response_status})'

    async def send_chatgpt_api_request(self, api_url, headers, data):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, headers=headers, json=data) as response:
                    response_data = await response.json()  # JSON 응답을 파싱
                    response_status = response.status  # HTTP 상태 코드 확인
                    return response_data, response_status
        except aiohttp.ClientConnectionError as e:
            # 연결 오류 처리
            print(f"Connection Error: {e}")
            return None, 0  # 연결 오류인 경우 상태 코드를 0으로 반환
        except aiohttp.ClientResponseError as e:
            # 클라이언트 응답 오류 처리
            print(f"Client Response Error: {e}")
            return None, e.status 

    # async def send_chatgpt_response(self, response):
    #     await self.send(text_data=json.dumps({
    #         'message': response
    #     }))