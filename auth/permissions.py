from rest_framework import permissions
from users.models import User


class IsActiveUser(permissions.BasePermission):
    """
    Permission to only allow active users.
    Checks if user status is active.
    """
    
    message = "Your account is not active."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if isinstance(request.user, User):
            return request.user.status == User.STATUS_ACTIVE
        
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Assumes the model instance has a `user` attribute.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.user == request.user


class IsProfileOwner(permissions.BasePermission):
    """
    Permission to only allow users to edit their own profile.
    """
    
    def has_object_permission(self, request, view, obj):
        # Check if the object is the same as the requesting user
        return obj == request.user


class PrivacyLevelPermission(permissions.BasePermission):
    """
    Permission based on user's privacy level.
    - Open: Anyone can view
    - Friends of Friends: Only friends and their friends can view
    - Private: Only the user can view
    """
    
    def has_object_permission(self, request, view, obj):
        # If object is not a User, allow
        if not isinstance(obj, User):
            return True
        
        # Owner can always access their own data
        if obj == request.user:
            return True
        
        # Check privacy level
        if obj.privacy_level == User.PRIVACY_OPEN:
            return True
        
        if obj.privacy_level == User.PRIVACY_PRIVATE:
            return False
        
        # For friends_of_friends, you would need to implement friend logic
        # This is a placeholder that defaults to False
        if obj.privacy_level == User.PRIVACY_FRIENDS_OF_FRIENDS:
            # TODO: Implement friend relationship checking
            # Example: return is_friend_or_friend_of_friend(request.user, obj)
            return False
        
        return False
