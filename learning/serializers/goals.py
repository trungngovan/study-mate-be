from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from learning.models import Goal, UserGoal


class GoalSerializer(serializers.ModelSerializer):
    """
    Base serializer for Goal model.
    """
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Goal
        fields = [
            "id",
            "code",
            "name",
            "type",
            "created_at",
            "updated_at",
            "user_count",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "user_count"]
    
    @extend_schema_field(serializers.IntegerField)
    def get_user_count(self, obj) -> int:
        """Return the number of users with this goal."""
        return obj.user_goals.count()


class GoalListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for Goal list view.
    """
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Goal
        fields = [
            "id",
            "code",
            "name",
            "type",
            "user_count",
        ]
        read_only_fields = ["id", "user_count"]
    
    @extend_schema_field(serializers.IntegerField)
    def get_user_count(self, obj) -> int:
        """Return the number of users with this goal."""
        return obj.user_goals.count()


class GoalDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Goal with statistics.
    """
    user_count = serializers.SerializerMethodField()
    avg_target_value = serializers.SerializerMethodField()
    
    class Meta:
        model = Goal
        fields = [
            "id",
            "code",
            "name",
            "type",
            "created_at",
            "updated_at",
            "user_count",
            "avg_target_value",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "user_count", "avg_target_value"]
    
    @extend_schema_field(serializers.IntegerField)
    def get_user_count(self, obj) -> int:
        """Return the number of users with this goal."""
        return obj.user_goals.count()
    
    @extend_schema_field(serializers.FloatField)
    def get_avg_target_value(self, obj):
        """Return the average target value for this goal."""
        from django.db.models import Avg
        result = obj.user_goals.aggregate(avg_value=Avg("target_value"))
        return float(result["avg_value"]) if result["avg_value"] else 0.0


class GoalCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating Goal.
    """
    class Meta:
        model = Goal
        fields = [
            "code",
            "name",
            "type",
        ]
    
    def validate_code(self, value):
        """Validate that code is unique (except for updates)."""
        if self.instance:
            # Update case - allow same code
            if Goal.objects.exclude(pk=self.instance.pk).filter(code=value).exists():
                raise serializers.ValidationError("Goal with this code already exists.")
        else:
            # Create case
            if Goal.objects.filter(code=value).exists():
                raise serializers.ValidationError("Goal with this code already exists.")
        return value


class UserGoalSerializer(serializers.ModelSerializer):
    """
    Serializer for UserGoal model.
    """
    goal_code = serializers.CharField(source="goal.code", read_only=True)
    goal_name = serializers.CharField(source="goal.name", read_only=True)
    goal_type = serializers.CharField(source="goal.type", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    
    class Meta:
        model = UserGoal
        fields = [
            "id",
            "user",
            "user_email",
            "goal",
            "goal_code",
            "goal_name",
            "goal_type",
            "target_value",
            "target_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "user_email", "goal_code", "goal_name", "goal_type", "created_at", "updated_at"]


class UserGoalListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for UserGoal list view.
    """
    goal_code = serializers.CharField(source="goal.code", read_only=True)
    goal_name = serializers.CharField(source="goal.name", read_only=True)
    
    class Meta:
        model = UserGoal
        fields = [
            "id",
            "goal",
            "goal_code",
            "goal_name",
            "target_value",
            "target_date",
        ]
        read_only_fields = ["id", "goal_code", "goal_name"]


class UserGoalDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for UserGoal.
    """
    goal_code = serializers.CharField(source="goal.code", read_only=True)
    goal_name = serializers.CharField(source="goal.name", read_only=True)
    goal_type = serializers.CharField(source="goal.type", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)
    
    class Meta:
        model = UserGoal
        fields = [
            "id",
            "user",
            "user_email",
            "user_full_name",
            "goal",
            "goal_code",
            "goal_name",
            "goal_type",
            "target_value",
            "target_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "user_email", "user_full_name", "goal_code", "goal_name", "goal_type", "created_at", "updated_at"]


class UserGoalCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating UserGoal.
    """
    class Meta:
        model = UserGoal
        fields = [
            "goal",
            "target_value",
            "target_date",
        ]
    
    def validate(self, attrs):
        """Validate unique constraint for user and goal."""
        user = self.context["request"].user
        goal = attrs.get("goal")
        
        if self.instance:
            # Update case
            if UserGoal.objects.exclude(pk=self.instance.pk).filter(user=user, goal=goal).exists():
                raise serializers.ValidationError("You have already added this goal.")
        else:
            # Create case
            if UserGoal.objects.filter(user=user, goal=goal).exists():
                raise serializers.ValidationError("You have already added this goal.")
        
        return attrs
    
    def create(self, validated_data):
        """Set user from request context."""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
