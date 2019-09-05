from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

from .utils import *


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        # self.scope['url_route']['kwargs']['room_name']
        self.room_name = "tradingData"
        self.room_group_name = "tradingData"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

        addUserToWS('Platform')

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        removeUserFromWS('Platform')

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        data = text_data_json['data']
        print("Message received: ", data)

    # Receive message from room group

    def broadcast(self, event):
        data = event['data']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'data': data
        }))


class CryptoConsumer(WebsocketConsumer):

    def connect(self):
        # self.scope['url_route']['kwargs']['room_name']
        self.room_name = "crypto"
        self.room_group_name = "crypto"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

        addUserToWS('Crypto')

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        removeUserFromWS('Crypto')

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        data = text_data_json['data']
        print("Message received: ", data)

    # Receive message from room group

    def broadcast(self, event):
        data = event['data']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'data': data
        }))
