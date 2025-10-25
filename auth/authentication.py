from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from users.models import User


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that works with the custom User model.
    """
    
    def get_user(self, validated_token):
        """
        Retrieve user from the validated JWT token.
        """
        try:
            user_id = validated_token.get('user_id')
            user = User.objects.get(id=user_id)
            
            # Check if user is active
            if user.status != User.STATUS_ACTIVE:
                raise AuthenticationFailed('User account is not active.')
            
            return user
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found.')
