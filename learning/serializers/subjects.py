from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from learning.models import Subject, UserSubject


class SubjectSerializer(serializers.ModelSerializer):
    """
    Base serializer for Subject model.
    """
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = [
            "id",
            "code",
            "name_vi",
            "name_en",
            "level",
            "created_at",
            "updated_at",
            "user_count",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "user_count"]
    
    @extend_schema_field(serializers.IntegerField)
    def get_user_count(self, obj) -> int:
        """Return the number of users studying this subject."""
        return obj.user_subjects.count()


class SubjectListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for Subject list view.
    """
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = [
            "id",
            "code",
            "name_vi",
            "name_en",
            "level",
            "user_count",
        ]
        read_only_fields = ["id", "user_count"]
    
    @extend_schema_field(serializers.IntegerField)
    def get_user_count(self, obj) -> int:
        """Return the number of users studying this subject."""
        return obj.user_subjects.count()


class SubjectDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Subject with user statistics.
    """
    user_count = serializers.SerializerMethodField()
    learners_count = serializers.SerializerMethodField()
    teachers_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = [
            "id",
            "code",
            "name_vi",
            "name_en",
            "level",
            "created_at",
            "updated_at",
            "user_count",
            "learners_count",
            "teachers_count",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "user_count", "learners_count", "teachers_count"]
    
    @extend_schema_field(serializers.IntegerField)
    def get_user_count(self, obj) -> int:
        """Return the total number of users for this subject."""
        return obj.user_subjects.count()
    
    @extend_schema_field(serializers.IntegerField)
    def get_learners_count(self, obj) -> int:
        """Return the number of learners for this subject."""
        return obj.user_subjects.filter(intent__in=["learn", "both"]).count()
    
    @extend_schema_field(serializers.IntegerField)
    def get_teachers_count(self, obj) -> int:
        """Return the number of teachers for this subject."""
        return obj.user_subjects.filter(intent__in=["teach", "both"]).count()


class SubjectCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating Subject.
    """
    class Meta:
        model = Subject
        fields = [
            "code",
            "name_vi",
            "name_en",
            "level",
        ]
    
    def validate_code(self, value):
        """Validate that code is unique (except for updates)."""
        if self.instance:
            # Update case - allow same code
            if Subject.objects.exclude(pk=self.instance.pk).filter(code=value).exists():
                raise serializers.ValidationError("Subject with this code already exists.")
        else:
            # Create case
            if Subject.objects.filter(code=value).exists():
                raise serializers.ValidationError("Subject with this code already exists.")
        return value


class UserSubjectSerializer(serializers.ModelSerializer):
    """
    Serializer for UserSubject model.
    """
    subject_code = serializers.CharField(source="subject.code", read_only=True)
    subject_name_vi = serializers.CharField(source="subject.name_vi", read_only=True)
    subject_name_en = serializers.CharField(source="subject.name_en", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    
    class Meta:
        model = UserSubject
        fields = [
            "id",
            "user",
            "user_email",
            "subject",
            "subject_code",
            "subject_name_vi",
            "subject_name_en",
            "level",
            "intent",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "user_email", "subject_code", "subject_name_vi", "subject_name_en", "created_at", "updated_at"]


class UserSubjectListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for UserSubject list view.
    """
    subject_code = serializers.CharField(source="subject.code", read_only=True)
    subject_name_en = serializers.CharField(source="subject.name_en", read_only=True)
    
    class Meta:
        model = UserSubject
        fields = [
            "id",
            "subject",
            "subject_code",
            "subject_name_en",
            "level",
            "intent",
        ]
        read_only_fields = ["id", "subject_code", "subject_name_en"]


class UserSubjectDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for UserSubject.
    """
    subject_code = serializers.CharField(source="subject.code", read_only=True)
    subject_name_vi = serializers.CharField(source="subject.name_vi", read_only=True)
    subject_name_en = serializers.CharField(source="subject.name_en", read_only=True)
    subject_level = serializers.CharField(source="subject.level", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_full_name = serializers.CharField(source="user.full_name", read_only=True)
    
    class Meta:
        model = UserSubject
        fields = [
            "id",
            "user",
            "user_email",
            "user_full_name",
            "subject",
            "subject_code",
            "subject_name_vi",
            "subject_name_en",
            "subject_level",
            "level",
            "intent",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "user_email", "user_full_name", "subject_code", "subject_name_vi", "subject_name_en", "subject_level", "created_at", "updated_at"]


class UserSubjectCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating UserSubject.
    """
    class Meta:
        model = UserSubject
        fields = [
            "subject",
            "level",
            "intent",
            "note",
        ]
    
    def validate(self, attrs):
        """Validate unique constraint for user and subject."""
        user = self.context["request"].user
        subject = attrs.get("subject")
        
        if self.instance:
            # Update case
            if UserSubject.objects.exclude(pk=self.instance.pk).filter(user=user, subject=subject).exists():
                raise serializers.ValidationError("You have already added this subject.")
        else:
            # Create case
            if UserSubject.objects.filter(user=user, subject=subject).exists():
                raise serializers.ValidationError("You have already added this subject.")
        
        return attrs
    
    def create(self, validated_data):
        """Set user from request context."""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
