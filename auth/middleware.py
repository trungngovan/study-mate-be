from django.utils.functional import SimpleLazyObject
from users.models import User


def get_user_from_request(request):
    """
    Get the user from the request object.
    This works with our custom User model and JWT authentication.
    """
    if not hasattr(request, '_cached_user'):
        # Use the authentication classes to get the user
        user = None
        if hasattr(request, 'user') and request.user:
            # If JWT authentication already set the user
            if isinstance(request.user, User):
                user = request.user
            else:
                # Anonymous user or other auth type
                user = request.user
        request._cached_user = user
    return request._cached_user


class CustomUserMiddleware:
    """
    Middleware that ensures request.user works with our custom User model.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Lazily get the user
        request.user = SimpleLazyObject(lambda: get_user_from_request(request))
        response = self.get_response(request)
        return response
