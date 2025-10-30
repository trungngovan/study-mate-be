from django.db import models
from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError
from django.utils import timezone
from users.models import User
from learning.models import Subject
from locations.models import School


class StudyGroup(models.Model):
    """
    Model representing a study group.
    Multiple users can join and collaborate on learning specific subjects.
    """

    # Privacy Level Choices
    PRIVACY_PUBLIC = "public"
    PRIVACY_PRIVATE = "private"
    PRIVACY_INVITE_ONLY = "invite_only"

    PRIVACY_CHOICES = [
        (PRIVACY_PUBLIC, "Public"),  # Anyone can join
        (PRIVACY_PRIVATE, "Private"),  # Anyone can see, must request to join
        (PRIVACY_INVITE_ONLY, "Invite Only"),  # Only visible to members, invite required
    ]

    # Status Choices
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_ARCHIVED = "archived"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    # Core Fields
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True, null=True, help_text="Group profile image URL")

    # Creator/Owner
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_groups')

    # School Association (optional)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True, related_name='study_groups')

    # Location (optional - for local groups)
    geom_point = gis_models.PointField(geography=True, null=True, blank=True, srid=4326, help_text="Geographic center of the group")

    # Subjects
    subjects = models.ManyToManyField(Subject, related_name='study_groups', blank=True)

    # Privacy & Access
    privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default=PRIVACY_PUBLIC)

    # Capacity
    max_members = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum number of members (null = unlimited)")

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'study_groups'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['privacy']),
            models.Index(fields=['status']),
            models.Index(fields=['school']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        """Get current number of active members"""
        return self.memberships.filter(status=GroupMembership.STATUS_ACTIVE).count()

    @property
    def is_full(self):
        """Check if group has reached max capacity"""
        if self.max_members is None:
            return False
        return self.member_count >= self.max_members

    def get_admins(self):
        """Get all admin members"""
        return User.objects.filter(
            group_memberships__group=self,
            group_memberships__role=GroupMembership.ROLE_ADMIN,
            group_memberships__status=GroupMembership.STATUS_ACTIVE
        )

    def is_admin(self, user):
        """Check if user is an admin of the group"""
        return self.memberships.filter(
            user=user,
            role=GroupMembership.ROLE_ADMIN,
            status=GroupMembership.STATUS_ACTIVE
        ).exists()

    def is_moderator(self, user):
        """Check if user is a moderator (or admin) of the group"""
        return self.memberships.filter(
            user=user,
            role__in=[GroupMembership.ROLE_ADMIN, GroupMembership.ROLE_MODERATOR],
            status=GroupMembership.STATUS_ACTIVE
        ).exists()

    def is_member(self, user):
        """Check if user is an active member"""
        return self.memberships.filter(
            user=user,
            status=GroupMembership.STATUS_ACTIVE
        ).exists()

    def can_join(self, user):
        """Check if a user can join the group"""
        if self.is_full:
            return False
        if self.status != self.STATUS_ACTIVE:
            return False
        if self.is_member(user):
            return False
        if self.privacy == self.PRIVACY_INVITE_ONLY:
            # Check if user has a pending invite
            return self.memberships.filter(
                user=user,
                status=GroupMembership.STATUS_INVITED
            ).exists()
        return True


class GroupMembership(models.Model):
    """
    Model representing a user's membership in a study group.
    Tracks role, status, and join date.
    """

    # Role Choices
    ROLE_ADMIN = "admin"
    ROLE_MODERATOR = "moderator"
    ROLE_MEMBER = "member"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_MODERATOR, "Moderator"),
        (ROLE_MEMBER, "Member"),
    ]

    # Status Choices
    STATUS_ACTIVE = "active"
    STATUS_PENDING = "pending"  # Requested to join
    STATUS_INVITED = "invited"  # Invited by admin
    STATUS_REMOVED = "removed"
    STATUS_LEFT = "left"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_PENDING, "Pending"),
        (STATUS_INVITED, "Invited"),
        (STATUS_REMOVED, "Removed"),
        (STATUS_LEFT, "Left"),
    ]

    # Core Fields
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    # Invitation/Request tracking
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_group_invites')

    # Metadata
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    left_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'group_memberships'
        unique_together = [['group', 'user']]
        ordering = ['joined_at']
        indexes = [
            models.Index(fields=['group', 'status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.group.name} ({self.role})"

    def clean(self):
        """Validate membership"""
        super().clean()

        # Ensure at least one admin exists if promoting/demoting
        if self.pk and self.role != self.ROLE_ADMIN:
            # Check if this is the last admin
            admin_count = GroupMembership.objects.filter(
                group=self.group,
                role=self.ROLE_ADMIN,
                status=self.STATUS_ACTIVE
            ).exclude(pk=self.pk).count()

            if admin_count == 0:
                # Check if current user was an admin
                old_membership = GroupMembership.objects.get(pk=self.pk)
                if old_membership.role == self.ROLE_ADMIN:
                    raise ValidationError("Cannot remove the last admin. Promote another member first.")

    def accept_invitation(self):
        """Accept an invitation to join the group"""
        if self.status == self.STATUS_INVITED:
            self.status = self.STATUS_ACTIVE
            self.save(update_fields=['status', 'updated_at'])

    def accept_request(self):
        """Accept a join request (admin action)"""
        if self.status == self.STATUS_PENDING:
            self.status = self.STATUS_ACTIVE
            self.save(update_fields=['status', 'updated_at'])

    def leave(self):
        """Leave the group"""
        self.status = self.STATUS_LEFT
        self.left_at = timezone.now()
        self.save(update_fields=['status', 'left_at', 'updated_at'])

    def remove(self):
        """Remove from group (admin action)"""
        self.status = self.STATUS_REMOVED
        self.left_at = timezone.now()
        self.save(update_fields=['status', 'left_at', 'updated_at'])


class GroupConversation(models.Model):
    """
    Model representing a conversation/chat for a study group.
    Extends the chat functionality to support group messaging.
    """

    # Core Fields
    group = models.OneToOneField(StudyGroup, on_delete=models.CASCADE, related_name='conversation')

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'group_conversations'

    def __str__(self):
        return f"Conversation for {self.group.name}"

    def is_participant(self, user):
        """Check if user is an active member of the group"""
        return self.group.is_member(user)


class GroupMessage(models.Model):
    """
    Model representing a message in a group conversation.
    Similar to regular Message but supports group context.
    """

    # Core Fields
    conversation = models.ForeignKey(GroupConversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_group_messages')
    content = models.TextField()

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'group_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender']),
        ]

    def __str__(self):
        return f"{self.sender.email}: {self.content[:50]}"

    def save(self, *args, **kwargs):
        """Override save to update conversation's last_message_at"""
        is_new = self.pk is None

        # Verify sender is a member
        if is_new and not self.conversation.is_participant(self.sender):
            raise ValidationError("Only group members can send messages.")

        super().save(*args, **kwargs)

        # Update conversation's last message time
        if is_new:
            self.conversation.last_message_at = self.created_at
            self.conversation.save(update_fields=['last_message_at'])


class GroupMessageRead(models.Model):
    """
    Model to track which messages have been read by which users.
    Allows for read receipts in group chats.
    """

    message = models.ForeignKey(GroupMessage, on_delete=models.CASCADE, related_name='read_by')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='read_group_messages')
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'group_message_reads'
        unique_together = [['message', 'user']]
        ordering = ['read_at']
        indexes = [
            models.Index(fields=['message']),
            models.Index(fields=['user', 'read_at']),
        ]

    def __str__(self):
        return f"{self.user.email} read message {self.message.pk}"
