import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationsConsumer(AsyncWebsocketConsumer):
    """Consumer to manage WebSocket connections for the Notification app,
    called when the websocket is handshaking as part of initial connection.
    """
    async def connect(self):
        """Consumer Connect implementation, to validate user status and prevent
        non authenticated user to take advante from the connection."""
        if self.scope["user"].is_anonymous:
            # Reject the connection
            await self.close()

        else:
            # Accept the connection
            await self.channel_layer.group_add(
                'notifications', self.channel_name)
            await self.channel_layer.group_add(
                f'{self.scope["user"]}-notification', self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        """Consumer implementation to leave behind the group at the moment the
        closes the connection."""
        await self.channel_layer.group_discard(
           'notifications', self.channel_name)
        await self.channel_layer.group_discard(
                f'{self.scope["user"]}-notification', self.channel_name)

    async def receive(self, text_data):
        """Receive method implementation to redirect any new message received
        on the websocket to broadcast to all the clients."""
        if isinstance(text_data, str):
            text_data = json.loads(text_data)
            user = text_data.get('caller')
            group_name  = f'{user}-notification'
            await self.channel_layer.group_send(group_name, text_data)
        else:
            await self.send(text_data=json.dumps(text_data))

    async def accept_call(self, event):
        event['key'] = 'AcceptCall'
        await self.send(text_data = json.dumps(event))

    async def reject_call(self, event):
        event['key'] = 'RejectCall'
        await self.send(text_data = json.dumps(event))
