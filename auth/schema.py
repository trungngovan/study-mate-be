"""
OpenAPI schema definitions for authentication endpoints.
"""
from drf_spectacular.utils import extend_schema
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer
)


class CustomJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    """
    OpenAPI extension for CustomJWTAuthentication.
    """
    target_class = 'auth.authentication.CustomJWTAuthentication'
    name = 'jwtAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }

# Schema decorators for each view
register_schema = extend_schema(
    summary="Register a new user",
    description="Create a new user account with email and password. Returns user profile and JWT tokens.",
    request=UserRegistrationSerializer,
    responses={
        201: {
            "type": "object",
            "properties": {
                "message": {"type": "string", "example": "User registered successfully"},
                "user": {"$ref": "#/components/schemas/UserProfile"},
                "tokens": {
                    "type": "object",
                    "properties": {
                        "refresh": {"type": "string"},
                        "access": {"type": "string"}
                    }
                }
            }
        },
        400: {
            "type": "object",
            "properties": {
                "error": {"type": "string"}
            }
        }
    },
    tags=["Authentication"]
)

login_schema = extend_schema(
    summary="User login",
    description="Authenticate user with email and password. Returns user profile and JWT tokens.",
    request=UserLoginSerializer,
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string", "example": "Login successful"},
                "user": {"$ref": "#/components/schemas/UserProfile"},
                "tokens": {
                    "type": "object",
                    "properties": {
                        "refresh": {"type": "string"},
                        "access": {"type": "string"}
                    }
                }
            }
        },
        400: {
            "type": "object",
            "properties": {
                "error": {"type": "string"}
            }
        }
    },
    tags=["Authentication"]
)

logout_schema = extend_schema(
    summary="User logout",
    description="Logout user by blacklisting the refresh token. Requires authentication.",
    request={
        "type": "object",
        "properties": {
            "refresh": {"type": "string", "description": "Refresh token to blacklist"}
        },
        "required": ["refresh"]
    },
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string", "example": "Logout successful"}
            }
        },
        400: {
            "type": "object",
            "properties": {
                "error": {"type": "string"}
            }
        }
    },
    tags=["Authentication"]
)

profile_get_schema = extend_schema(
    summary="Get user profile",
    description="Retrieve the current authenticated user's profile information.",
    responses={200: UserProfileSerializer},
    tags=["User Profile"]
)

profile_update_schema = extend_schema(
    summary="Update user profile",
    description="Update the current authenticated user's profile information (full update).",
    request=UserProfileSerializer,
    responses={200: UserProfileSerializer},
    tags=["User Profile"]
)

profile_partial_update_schema = extend_schema(
    summary="Partial update user profile",
    description="Partially update the current authenticated user's profile information.",
    request=UserProfileSerializer,
    responses={200: UserProfileSerializer},
    tags=["User Profile"]
)

change_password_schema = extend_schema(
    summary="Change password",
    description="Change the current authenticated user's password. Requires old password verification.",
    request=ChangePasswordSerializer,
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string", "example": "Password changed successfully"}
            }
        },
        400: {
            "type": "object",
            "properties": {
                "error": {"type": "string"}
            }
        }
    },
    tags=["User Profile"]
)
