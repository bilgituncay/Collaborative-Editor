import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Document
import asyncio

class EditorConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.document_id = self.scope['url_route']['kwargs']['document_id']
        self.room_group_name = f'editor_{self.document_id}'
        self.user_id = self.scope['user'].id if self.scope['user'].is_authenticated else 'anonymous'

        # Join room group

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send current document content
        content = await self.get_document_content()
        await self.send(text_data=json.dumps({
            'type': 'document_content',
            'content': content,
            'user_id': self.user_id
        }))

        # Notify others of new user
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': self.user_id
            }
        )

    async def disconnect(self, close_code):
        # Notify others that the user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user_id': self.user_id
            }
        )

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type')

        if msg_type == 'text_change':
            await self.handle_text_change(data)
        elif msg_type == 'cursor_position':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'cursor_update',
                    'user_id': self.user_id,
                    'position': data['position'],
                    'selection': data.get('selection')
                }
            )
    
    async def handle_text_change(self, data):
        operation = data['operation'] # Insert, delete or replace
        position = data['position']
        text = data.get('text', '')
        length = data.get('length', 0)

        # Save to database
        await self.save_document_content(data['content'])

        # Broadcast to all users except the sender

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast_text_change',
                'user_id': self.user_id,
                'operation': operation,
                'position': position,
                'text': text,
                'length': length,
                'content': data['content']
            }
        )

    # Message handlers called by channel layer when group_send is used
    async def broadcast_text_change(self, event):
        if event['user_id'] != self.user_id:
            await self.send(text_data=json.dumps({
                'type': 'text_change',
                'user_id': event['user_id'],
                'operation': event['operation'],
                'position': event['position'],
                'text': event['text'],
                'length': event['length'],
                'content': event['content']
            }))
    
    async def cursor_update(self, event):
        if event['user_id'] != self.user_id:
            await self.send(text_data=json.dumps({
                'type': 'cursor_position',
                'user_id': event['user_id'],
                'position': event['position'],
                'selection': event.get('selection')
            }))

    async def user_joined(self, event):
        if event['user_id'] != self.user_id:
            await self.send(text_data=json.dumps({
                'type': 'user_joined',
                'user_id': event['user_id']
            }))
    
    async def user_left(self, event):
        if event['user_left'] != self.user_id:
            await self.send(text_data=json.dumps({
                'type': 'user_left',
                'user_id': event['user_id']
            }))

    @database_sync_to_async
    def save_document_content(self, content):
        try:
            doc = Document.objects.get(id=self.document_id)
            doc.content = content
            doc.save()
        except Document.DoesNotExist:
            pass