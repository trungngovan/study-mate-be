from django.contrib import admin
from chat.models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Admin interface for Conversation model."""
    
    list_display = [
        'id',
        'get_participants_display',
        'last_message_at',
        'created_at',
    ]
    
    list_filter = [
        'created_at',
        'last_message_at',
    ]
    
    search_fields = [
        'connection__user1__email',
        'connection__user1__full_name',
        'connection__user2__email',
        'connection__user2__full_name',
    ]
    
    readonly_fields = [
        'connection',
        'last_message_at',
        'created_at',
        'updated_at',
    ]
    
    list_per_page = 25
    
    fieldsets = (
        ('Connection Info', {
            'fields': ('connection',)
        }),
        ('Timestamps', {
            'fields': ('last_message_at', 'created_at', 'updated_at')
        }),
    )
    
    def get_participants_display(self, obj):
        """Display conversation participants."""
        return f"{obj.connection.user1.full_name} <-> {obj.connection.user2.full_name}"
    get_participants_display.short_description = 'Participants'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('connection__user1', 'connection__user2')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model."""
    
    list_display = [
        'id',
        'get_sender_display',
        'get_conversation_display',
        'get_content_preview',
        'is_read',
        'created_at',
    ]
    
    list_filter = [
        'created_at',
        'read_at',
    ]
    
    search_fields = [
        'sender__email',
        'sender__full_name',
        'content',
        'conversation__connection__user1__email',
        'conversation__connection__user2__email',
    ]
    
    readonly_fields = [
        'conversation',
        'sender',
        'content',
        'read_at',
        'created_at',
        'updated_at',
    ]
    
    list_per_page = 50
    
    fieldsets = (
        ('Message Info', {
            'fields': ('conversation', 'sender', 'content')
        }),
        ('Status', {
            'fields': ('read_at',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def get_sender_display(self, obj):
        """Display sender name."""
        return obj.sender.full_name
    get_sender_display.short_description = 'Sender'
    
    def get_conversation_display(self, obj):
        """Display conversation participants."""
        return f"{obj.conversation.connection.user1.full_name} <-> {obj.conversation.connection.user2.full_name}"
    get_conversation_display.short_description = 'Conversation'
    
    def get_content_preview(self, obj):
        """Display first 50 characters of content."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    get_content_preview.short_description = 'Content'
    
    def is_read(self, obj):
        """Display read status."""
        return obj.is_read()
    is_read.boolean = True
    is_read.short_description = 'Read'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related(
            'sender',
            'conversation__connection__user1',
            'conversation__connection__user2'
        )


