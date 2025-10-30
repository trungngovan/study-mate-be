from django.contrib import admin
from .models import StudyGroup, GroupMembership, GroupConversation, GroupMessage, GroupMessageRead


@admin.register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    """Admin interface for StudyGroup model."""

    list_display = [
        'id',
        'name',
        'created_by',
        'privacy',
        'status',
        'member_count',
        'school',
        'created_at',
    ]

    list_filter = [
        'privacy',
        'status',
        'created_at',
        'school',
    ]

    search_fields = [
        'name',
        'description',
        'created_by__email',
        'created_by__full_name',
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
        'member_count',
        'is_full',
    ]

    filter_horizontal = ['subjects']

    list_per_page = 25

    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'description', 'avatar_url', 'created_by')
        }),
        ('Location & School', {
            'fields': ('school', 'geom_point')
        }),
        ('Subjects', {
            'fields': ('subjects',)
        }),
        ('Settings', {
            'fields': ('privacy', 'status', 'max_members', 'member_count', 'is_full')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('created_by', 'school').prefetch_related('subjects')


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    """Admin interface for GroupMembership model."""

    list_display = [
        'id',
        'user',
        'group',
        'role',
        'status',
        'invited_by',
        'joined_at',
    ]

    list_filter = [
        'role',
        'status',
        'joined_at',
    ]

    search_fields = [
        'user__email',
        'user__full_name',
        'group__name',
    ]

    readonly_fields = [
        'joined_at',
        'updated_at',
        'left_at',
    ]

    list_per_page = 25

    fieldsets = (
        ('Membership Info', {
            'fields': ('group', 'user', 'role', 'status')
        }),
        ('Invitation', {
            'fields': ('invited_by',)
        }),
        ('Timestamps', {
            'fields': ('joined_at', 'updated_at', 'left_at')
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('group', 'user', 'invited_by')


@admin.register(GroupConversation)
class GroupConversationAdmin(admin.ModelAdmin):
    """Admin interface for GroupConversation model."""

    list_display = [
        'id',
        'group',
        'created_at',
        'last_message_at',
    ]

    list_filter = [
        'created_at',
        'last_message_at',
    ]

    search_fields = [
        'group__name',
    ]

    readonly_fields = [
        'created_at',
        'last_message_at',
    ]

    list_per_page = 25

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('group')


@admin.register(GroupMessage)
class GroupMessageAdmin(admin.ModelAdmin):
    """Admin interface for GroupMessage model."""

    list_display = [
        'id',
        'conversation',
        'sender',
        'content_preview',
        'created_at',
    ]

    list_filter = [
        'created_at',
    ]

    search_fields = [
        'sender__email',
        'sender__full_name',
        'content',
        'conversation__group__name',
    ]

    readonly_fields = [
        'created_at',
    ]

    list_per_page = 25

    def content_preview(self, obj):
        """Show first 50 characters of message content"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('conversation', 'conversation__group', 'sender')


@admin.register(GroupMessageRead)
class GroupMessageReadAdmin(admin.ModelAdmin):
    """Admin interface for GroupMessageRead model."""

    list_display = [
        'id',
        'message',
        'user',
        'read_at',
    ]

    list_filter = [
        'read_at',
    ]

    search_fields = [
        'user__email',
        'user__full_name',
    ]

    readonly_fields = [
        'read_at',
    ]

    list_per_page = 25

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        queryset = super().get_queryset(request)
        return queryset.select_related('message', 'message__conversation', 'user')
