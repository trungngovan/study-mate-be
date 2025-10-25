from django.contrib.auth.backends import BaseBackend
from users.models import User


class CustomUserBackend(BaseBackend):
    """
    Custom authentication backend for the custom User model.
    Authenticates using email and password.
    """
    
    def authenticate(self, request, email=None, password=None, **kwargs):
        """
        Authenticate a user based on email and password.
        """
        try:
            user = User.objects.get(email=email)
            # Use check_password from AbstractBaseUser
            if user.check_password(password):
                if user.status == User.STATUS_ACTIVE:
                    return user
        except User.DoesNotExist:
            return None
        return None
    
    def get_user(self, user_id):
        """
        Get a user instance from the user_id.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
