import json

from channels.generic.websocket import AsyncWebsocketConsumer
# from asgiref.sync import async_to_sync


class MessagerConsumer(AsyncWebsocketConsumer):
    """Consumer to manage WebSocket connections for the Messager app.
    """
    async def connect(self):
        """Consumer Connect implementation, to validate user status and prevent
        non authenticated user to take advante from the connection."""
        if self.scope["user"].is_anonymous:
            # Reject the connection
            await self.close()

        else:
            # Accept the connection
            await self.channel_layer.group_add(f"{self.scope['user'].username}", self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        """Consumer implementation to leave behind the group at the moment the
        closes the connection."""
        await self.channel_layer.group_discard(f"{self.scope['user'].username}", self.channel_name)

    async def receive(self, text_data):
        """Receive method implementation to redirect any new message received
        on the websocket to broadcast to all the clients."""
        await self.send(text_data=json.dumps(text_data))


class VideoCallConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            await self.channel_layer.group_add(f'{self.scope["user"].username}-video-call', self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(f'{self.scope["user"].username}-video-call', self.channel_name)
        await self.close()

    async def receive(self, text_data):
        data = json.loads(text_data)
        target = data.get("target")
        await self.channel_layer.group_send(f'{target}-video-call', data)

    async def video_offer(self, text_data):
        await self.send(text_data=json.dumps(text_data))

    async def video_answer(self, text_data):
        await self.send(text_data=json.dumps(text_data))

    async def new_ice_candidate(self, text_data):
        await self.send(text_data=json.dumps(text_data))

    async def hang_up(self, text_data):
        await self.send(text_data=json.dumps(text_data))
