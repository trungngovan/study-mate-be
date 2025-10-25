from django.contrib import admin
from learning.models import Subject, UserSubject, Goal, UserGoal


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Admin configuration for Subject model."""
    list_display = ["id", "code", "name_en", "name_vi", "level", "created_at"]
    list_filter = ["level", "created_at"]
    search_fields = ["code", "name_en", "name_vi"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(UserSubject)
class UserSubjectAdmin(admin.ModelAdmin):
    """Admin configuration for UserSubject model."""
    list_display = ["id", "user", "subject", "level", "intent", "created_at"]
    list_filter = ["level", "intent", "created_at"]
    search_fields = ["user__email", "user__full_name", "subject__code", "subject__name_en"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]
    raw_id_fields = ["user", "subject"]


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    """Admin configuration for Goal model."""
    list_display = ["id", "code", "name", "type", "created_at"]
    list_filter = ["type", "created_at"]
    search_fields = ["code", "name"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(UserGoal)
class UserGoalAdmin(admin.ModelAdmin):
    """Admin configuration for UserGoal model."""
    list_display = ["id", "user", "goal", "target_value", "target_date", "created_at"]
    list_filter = ["target_date", "created_at"]
    search_fields = ["user__email", "user__full_name", "goal__code", "goal__name"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]
    raw_id_fields = ["user", "goal"]

