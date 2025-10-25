from django.contrib import admin
from .models import ConnectionRequest, Connection


@admin.register(ConnectionRequest)
class ConnectionRequestAdmin(admin.ModelAdmin):
    """Admin interface for ConnectionRequest model."""
    
    list_display = [
        'id',
        'sender',
        'receiver',
        'state',
        'created_at',
        'accepted_at',
    ]
    
    list_filter = [
        'state',
        'created_at',
        'accepted_at',
    ]
    
    search_fields = [
        'sender__email',
        'sender__full_name',
        'receiver__email',
        'receiver__full_name',
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'accepted_at',
        'rejected_at',
    ]
    
    list_per_page = 25
    
    fieldsets = (
        ('Connection Info', {
            'fields': ('sender', 'receiver', 'state', 'message')
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
                'accepted_at',
                'rejected_at',
            )
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('sender', 'receiver')


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    """Admin interface for Connection model."""
    
    list_display = [
        'id',
        'user1',
        'user2',
        'created_at',
    ]
    
    list_filter = [
        'created_at',
    ]
    
    search_fields = [
        'user1__email',
        'user1__full_name',
        'user2__email',
        'user2__full_name',
    ]
    
    readonly_fields = [
        'created_at',
    ]
    
    list_per_page = 25
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('user1', 'user2', 'connection_request')
