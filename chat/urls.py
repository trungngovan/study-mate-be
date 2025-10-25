from django.urls import path, include
from rest_framework.routers import DefaultRouter
from chat.views import ConversationViewSet, MessageViewSet

app_name = 'chat'

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
]


