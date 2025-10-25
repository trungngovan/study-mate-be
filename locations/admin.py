from django.contrib import admin
from .models import School, City, LocationHistory


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("name",)
        }),
        ("Location", {
            "fields": ("geom_point",)
        }),
    )


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ["name", "short_name", "city", "created_at"]
    list_filter = ["city", "created_at"]
    search_fields = ["name", "short_name", "address"]
    readonly_fields = ["created_at", "updated_at"]
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "short_name")
        }),
        ("Location", {
            "fields": ("address", "city", "geom_point")
        }),
        ("Contact", {
            "fields": ("website", "email", "phone")
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(LocationHistory)
class LocationHistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "get_location", "recorded_at", "accuracy", "created_at"]
    list_filter = ["recorded_at", "created_at"]
    search_fields = ["user__email", "user__full_name"]
    readonly_fields = ["created_at", "recorded_at"]
    date_hierarchy = "recorded_at"
    
    fieldsets = (
        ("User Information", {
            "fields": ("user",)
        }),
        ("Location Data", {
            "fields": ("geom_point", "accuracy")
        }),
        ("Timestamps", {
            "fields": ("recorded_at", "created_at"),
        }),
    )
    
    def get_location(self, obj):
        """Display location coordinates."""
        if obj.geom_point:
            return f"({obj.geom_point.y:.6f}, {obj.geom_point.x:.6f})"
        return "N/A"
    get_location.short_description = "Location (Lat, Lng)"
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related("user")

