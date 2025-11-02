"""
Permissions for groups app.
"""
from rest_framework import permissions


class IsGroupAdmin(permissions.BasePermission):
    """
    Permission to only allow group admins to perform certain actions.
    """

    message = "Only group admins can perform this action."

    def has_object_permission(self, request, view, obj):
        # For StudyGroup objects
        if hasattr(obj, 'is_admin'):
            return obj.is_admin(request.user)
        # For GroupMembership objects
        elif hasattr(obj, 'group'):
            return obj.group.is_admin(request.user)
        return False


class IsGroupModerator(permissions.BasePermission):
    """
    Permission to only allow group moderators (or admins) to perform certain actions.
    """

    message = "Only group moderators or admins can perform this action."

    def has_object_permission(self, request, view, obj):
        # For StudyGroup objects
        if hasattr(obj, 'is_moderator'):
            return obj.is_moderator(request.user)
        # For GroupMembership objects
        elif hasattr(obj, 'group'):
            return obj.group.is_moderator(request.user)
        return False


class IsGroupMember(permissions.BasePermission):
    """
    Permission to only allow group members to access certain resources.
    """

    message = "You must be a group member to perform this action."

    def has_object_permission(self, request, view, obj):
        # For StudyGroup objects
        if hasattr(obj, 'is_member'):
            return obj.is_member(request.user)
        # For GroupConversation objects
        elif hasattr(obj, 'is_participant'):
            return obj.is_participant(request.user)
        # For GroupMembership objects
        elif hasattr(obj, 'group'):
            return obj.group.is_member(request.user)
        # For GroupMessage objects
        elif hasattr(obj, 'conversation'):
            return obj.conversation.is_participant(request.user)
        return False


class IsGroupAdminOrReadOnly(permissions.BasePermission):
    """
    Permission that allows anyone to view but only admins to edit.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to admins
        if hasattr(obj, 'is_admin'):
            return obj.is_admin(request.user)
        elif hasattr(obj, 'group'):
            return obj.group.is_admin(request.user)
        return False


class CanJoinGroup(permissions.BasePermission):
    """
    Permission to check if a user can join a group.
    """

    message = "You cannot join this group."

    def has_object_permission(self, request, view, obj):
        return obj.can_join(request.user)


class IsMembershipOwner(permissions.BasePermission):
    """
    Permission to only allow the user themselves to manage their own membership.
    (e.g., leaving a group)
    """

    message = "You can only manage your own membership."

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
