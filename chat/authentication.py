import logging
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from users.models import User

logger = logging.getLogger(__name__)


@database_sync_to_async
def get_user_from_token(token_string):
    """
    Get user from JWT token for WebSocket authentication.
    """
    try:
        access_token = AccessToken(token_string)
        user_id = access_token.get('user_id')
        
        if user_id:
            user = User.objects.get(id=user_id)
            if user.status == User.STATUS_ACTIVE:
                logger.debug(f"WebSocket auth successful for user {user.id}")
                return user
            else:
                logger.warning(f"WebSocket auth failed: User {user.id} is not active (status={user.status})")
    except (InvalidToken, TokenError) as e:
        logger.warning(f"WebSocket auth failed: Invalid token - {type(e).__name__}: {str(e)}")
    except User.DoesNotExist:
        logger.warning(f"WebSocket auth failed: User with id {user_id} does not exist")
    
    return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """
    Custom middleware for JWT authentication in WebSocket connections.
    Extracts token from query string or headers.
    """
    
    async def __call__(self, scope, receive, send):
        # Get token from query string
        query_string = scope.get('query_string', b'').decode()
        token = None
        
        # Try to extract token from query string
        if 'token=' in query_string:
            for param in query_string.split('&'):
                if param.startswith('token='):
                    token = param.split('=', 1)[1]  # Split only on first '=' to handle tokens with '=' padding
                    logger.debug(f"Token extracted from query string (length={len(token)})")
                    break
        
        # If no token in query string, try headers
        if not token:
            headers = dict(scope.get('headers', []))
            auth_header = headers.get(b'authorization', b'').decode()
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
                logger.debug(f"Token extracted from Authorization header (length={len(token)})")
        
        # Authenticate user
        if token:
            scope['user'] = await get_user_from_token(token)
        else:
            logger.warning("No token found in query string or headers for WebSocket connection")
            scope['user'] = AnonymousUser()
        
        return await super().__call__(scope, receive, send)


def JWTAuthMiddlewareStack(inner):
    """
    Convenience function to wrap WebSocket consumers with JWT authentication.
    """
    return JWTAuthMiddleware(inner)


