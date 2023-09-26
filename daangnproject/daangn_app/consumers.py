import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # WebSocket 연결을 수락합니다.
        await self.accept()

    async def disconnect(self, close_code):
        # WebSocket 연결이 끊어질 때 실행되는 메서드입니다.
        pass

    async def receive(self, text_data):
        # 클라이언트로부터 메시지를 받을 때 실행되는 메서드입니다.
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # 메시지를 처리하고 다시 클라이언트에게 전송합니다.
        await self.send(text_data=json.dumps({'message': message}))
