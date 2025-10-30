"""
Permissions for sessions app.
"""
from rest_framework import permissions


class IsSessionHost(permissions.BasePermission):
    """
    Permission to only allow the host of a session to modify it.
    """

    message = "Only the session host can perform this action."

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the host
        return obj.host == request.user


class IsSessionHostOrReadOnly(permissions.BasePermission):
    """
    Permission that allows anyone to view but only host to edit.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the host
        return obj.host == request.user


class IsSessionParticipant(permissions.BasePermission):
    """
    Permission to only allow participants of a session to access participant-specific actions.
    """

    message = "You are not a participant in this session."

    def has_object_permission(self, request, view, obj):
        # Check if user is a participant (for SessionParticipant objects)
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # Check if user is a participant (for StudySession objects)
        elif hasattr(obj, 'participants'):
            from .models import SessionParticipant
            return obj.participants.filter(
                user=request.user,
                status__in=[SessionParticipant.STATUS_REGISTERED, SessionParticipant.STATUS_ATTENDED]
            ).exists()
        return False


class CanJoinSession(permissions.BasePermission):
    """
    Permission to check if a user can join a session.
    """

    message = "You cannot join this session."

    def has_object_permission(self, request, view, obj):
        return obj.can_join(request.user)
