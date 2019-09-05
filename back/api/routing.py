from django.urls import path

from . import consumers

websocket_urlpatterns = [
    # path('ws/api/chat/<str:room_name>/', consumers.ChatConsumer),
    path('ws/api/tradingData/', consumers.ChatConsumer),
    path('ws/api/crypto/', consumers.CryptoConsumer),
]
