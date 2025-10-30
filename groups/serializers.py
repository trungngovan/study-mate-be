"""
Serializers for groups app.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point

from .models import StudyGroup, GroupMembership, GroupConversation, GroupMessage, GroupMessageRead
from learning.models import Subject
from locations.models import School


User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user information for groups."""

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'full_name',
            'avatar_url',
            'school',
            'major',
            'year',
        ]
        read_only_fields = fields


class SubjectBasicSerializer(serializers.ModelSerializer):
    """Basic subject information."""

    class Meta:
        model = Subject
        fields = ['id', 'code', 'name_en', 'name_vi', 'level']
        read_only_fields = fields


class SchoolBasicSerializer(serializers.ModelSerializer):
    """Basic school information."""

    class Meta:
        model = School
        fields = ['id', 'name', 'short_name']
        read_only_fields = fields


class GroupMembershipSerializer(serializers.ModelSerializer):
    """Serializer for group membership details."""

    user = UserBasicSerializer(read_only=True)
    invited_by = UserBasicSerializer(read_only=True)

    class Meta:
        model = GroupMembership
        fields = [
            'id',
            'user',
            'role',
            'status',
            'invited_by',
            'joined_at',
            'updated_at',
            'left_at',
        ]
        read_only_fields = fields


class StudyGroupListSerializer(serializers.ModelSerializer):
    """Serializer for study group list view (lightweight)."""

    created_by = UserBasicSerializer(read_only=True)
    school = SchoolBasicSerializer(read_only=True)
    subjects = SubjectBasicSerializer(many=True, read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    is_member = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = StudyGroup
        fields = [
            'id',
            'name',
            'description',
            'avatar_url',
            'created_by',
            'school',
            'subjects',
            'privacy',
            'member_count',
            'max_members',
            'is_full',
            'status',
            'is_member',
            'is_admin',
            'created_at',
        ]
        read_only_fields = fields

    def get_is_member(self, obj):
        """Check if current user is a member."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_member(request.user)
        return False

    def get_is_admin(self, obj):
        """Check if current user is an admin."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_admin(request.user)
        return False


class StudyGroupDetailSerializer(serializers.ModelSerializer):
    """Serializer for study group detail view (complete)."""

    created_by = UserBasicSerializer(read_only=True)
    school = SchoolBasicSerializer(read_only=True)
    subjects = SubjectBasicSerializer(many=True, read_only=True)
    memberships = GroupMembershipSerializer(many=True, read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    is_member = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    is_moderator = serializers.SerializerMethodField()
    can_join = serializers.SerializerMethodField()
    user_membership = serializers.SerializerMethodField()

    class Meta:
        model = StudyGroup
        fields = [
            'id',
            'name',
            'description',
            'avatar_url',
            'created_by',
            'school',
            'geom_point',
            'subjects',
            'privacy',
            'max_members',
            'member_count',
            'is_full',
            'status',
            'memberships',
            'is_member',
            'is_admin',
            'is_moderator',
            'can_join',
            'user_membership',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_by',
            'member_count',
            'is_full',
            'memberships',
            'is_member',
            'is_admin',
            'is_moderator',
            'can_join',
            'user_membership',
            'created_at',
            'updated_at',
        ]

    def get_is_member(self, obj):
        """Check if current user is a member."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_member(request.user)
        return False

    def get_is_admin(self, obj):
        """Check if current user is an admin."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_admin(request.user)
        return False

    def get_is_moderator(self, obj):
        """Check if current user is a moderator."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_moderator(request.user)
        return False

    def get_can_join(self, obj):
        """Check if current user can join the group."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.can_join(request.user)
        return False

    def get_user_membership(self, obj):
        """Get current user's membership info."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            membership = obj.memberships.filter(user=request.user).first()
            if membership:
                return GroupMembershipSerializer(membership).data
        return None


class CreateStudyGroupSerializer(serializers.ModelSerializer):
    """Serializer for creating a study group."""

    subject_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )
    latitude = serializers.FloatField(required=False, write_only=True)
    longitude = serializers.FloatField(required=False, write_only=True)

    class Meta:
        model = StudyGroup
        fields = [
            'name',
            'description',
            'avatar_url',
            'school',
            'subject_ids',
            'latitude',
            'longitude',
            'privacy',
            'max_members',
        ]

    def create(self, validated_data):
        """Create group with creator as admin."""
        subject_ids = validated_data.pop('subject_ids', [])
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)

        # Set creator
        validated_data['created_by'] = self.context['request'].user

        # Create geom_point if coordinates provided
        if latitude is not None and longitude is not None:
            validated_data['geom_point'] = Point(longitude, latitude, srid=4326)

        # Create group
        group = super().create(validated_data)

        # Add subjects
        if subject_ids:
            group.subjects.set(subject_ids)

        # Create admin membership for creator
        GroupMembership.objects.create(
            group=group,
            user=self.context['request'].user,
            role=GroupMembership.ROLE_ADMIN,
            status=GroupMembership.STATUS_ACTIVE
        )

        # Create group conversation
        GroupConversation.objects.create(group=group)

        return group


class UpdateStudyGroupSerializer(serializers.ModelSerializer):
    """Serializer for updating a study group (admin only)."""

    subject_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )
    latitude = serializers.FloatField(required=False, write_only=True)
    longitude = serializers.FloatField(required=False, write_only=True)

    class Meta:
        model = StudyGroup
        fields = [
            'name',
            'description',
            'avatar_url',
            'school',
            'subject_ids',
            'latitude',
            'longitude',
            'privacy',
            'max_members',
            'status',
        ]

    def update(self, instance, validated_data):
        """Update group with optional subjects and coordinates."""
        subject_ids = validated_data.pop('subject_ids', None)
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)

        # Update coordinates if provided
        if latitude is not None and longitude is not None:
            validated_data['geom_point'] = Point(longitude, latitude, srid=4326)

        # Update group
        group = super().update(instance, validated_data)

        # Update subjects if provided
        if subject_ids is not None:
            group.subjects.set(subject_ids)

        return group


class JoinGroupSerializer(serializers.Serializer):
    """Serializer for joining a group."""
    pass  # No fields needed for public groups


class InviteUserSerializer(serializers.Serializer):
    """Serializer for inviting a user to a group."""

    user_id = serializers.IntegerField()

    def validate_user_id(self, value):
        """Validate that user exists."""
        try:
            User.objects.get(pk=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
        return value


class UpdateMemberRoleSerializer(serializers.Serializer):
    """Serializer for updating a member's role."""

    role = serializers.ChoiceField(choices=GroupMembership.ROLE_CHOICES)


class GroupMessageSerializer(serializers.ModelSerializer):
    """Serializer for group messages."""

    sender = UserBasicSerializer(read_only=True)
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = GroupMessage
        fields = [
            'id',
            'conversation',
            'sender',
            'content',
            'is_read',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'conversation',
            'sender',
            'is_read',
            'created_at',
        ]

    def get_is_read(self, obj):
        """Check if current user has read this message."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return GroupMessageRead.objects.filter(
                message=obj,
                user=request.user
            ).exists()
        return False


class CreateGroupMessageSerializer(serializers.ModelSerializer):
    """Serializer for creating a group message."""

    class Meta:
        model = GroupMessage
        fields = ['content']

    def create(self, validated_data):
        """Create message with sender and conversation from context."""
        validated_data['sender'] = self.context['request'].user
        validated_data['conversation'] = self.context['conversation']
        return super().create(validated_data)


class MarkMessagesReadSerializer(serializers.Serializer):
    """Serializer for marking messages as read."""

    message_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
