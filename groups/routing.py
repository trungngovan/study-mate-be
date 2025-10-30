from django.urls import re_path
from groups.consumers import GroupChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/groups/(?P<group_id>\d+)/chat/$', GroupChatConsumer.as_asgi()),
]
