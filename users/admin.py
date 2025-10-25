from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin for User model based on Django"s UserAdmin.
    """
    list_display = ["email", "full_name", "status_badge", "school", "is_staff", "last_active_at", "created_at"]
    list_filter = ["status", "is_staff", "is_superuser", "is_active", "privacy_level", "school"]
    search_fields = ["email", "full_name", "phone"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"
    
    fieldsets = (
        ("Authentication", {
            "fields": ("email", "password")
        }),
        ("Personal Information", {
            "fields": ("full_name", "phone", "bio", "avatar_url")
        }),
        ("Academic Information", {
            "fields": ("school", "major", "year")
        }),
        ("Location & Preferences", {
            "fields": ("learning_radius_km", "geom_last_point", "privacy_level")
        }),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "status", "groups", "user_permissions")
        }),
        ("Important Dates", {
            "fields": ("last_login", "last_active_at", "created_at", "updated_at")
        }),
    )
    
    add_fieldsets = (
        ("Create New User", {
            "classes": ("wide",),
            "fields": ("email", "full_name", "password1", "password2", "is_staff", "is_superuser"),
        }),
    )
    
    readonly_fields = ["created_at", "updated_at", "last_login", "last_active_at"]
    
    def status_badge(self, obj):
        """Display status as a colored badge."""
        colors = {
            "active": "green",
            "banned": "red",
            "deleted": "gray",
        }
        color = colors.get(obj.status, "gray")
        return format_html(
            "<span style='background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;'>{}</span>",
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Status"
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related("school")

