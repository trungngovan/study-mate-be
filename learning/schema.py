"""
OpenAPI schema definitions for learning endpoints.
"""
from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers
from learning.serializers import (
    SubjectListSerializer,
    SubjectDetailSerializer,
    SubjectCreateUpdateSerializer,
    UserSubjectListSerializer,
    UserSubjectDetailSerializer,
    UserSubjectCreateUpdateSerializer,
    GoalListSerializer,
    GoalDetailSerializer,
    GoalCreateUpdateSerializer,
    UserGoalListSerializer,
    UserGoalDetailSerializer,
    UserGoalCreateUpdateSerializer,
)


# Schema for error response
ErrorResponseSerializer = inline_serializer(
    name='LearningErrorResponse',
    fields={
        'error': serializers.CharField(),
    }
)


# Subject List/Create schemas
subject_list_schema = extend_schema(
    summary="List subjects",
    description="Get a paginated list of subjects. Supports search and filtering.",
    parameters=[
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search subjects by code, name_vi, or name_en"
        ),
        OpenApiParameter(
            name="level",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter subjects by level (beginner, intermediate, advanced, expert)"
        ),
        OpenApiParameter(
            name="ordering",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Order results by: code, name_en, created_at (prefix with - for descending)"
        ),
    ],
    responses={200: SubjectListSerializer(many=True)},
    tags=["Subjects"]
)

subject_create_schema = extend_schema(
    summary="Create a subject",
    description="Create a new subject. Requires authentication.",
    request=SubjectCreateUpdateSerializer,
    responses={201: SubjectCreateUpdateSerializer},
    tags=["Subjects"]
)


# Subject Retrieve/Update/Destroy schemas
subject_retrieve_schema = extend_schema(
    summary="Get subject details",
    description="Retrieve detailed information about a specific subject including user statistics.",
    responses={200: SubjectDetailSerializer},
    tags=["Subjects"]
)

subject_update_schema = extend_schema(
    summary="Update subject (full)",
    description="Fully update a subject's information. Requires authentication.",
    request=SubjectCreateUpdateSerializer,
    responses={200: SubjectCreateUpdateSerializer},
    tags=["Subjects"]
)

subject_partial_update_schema = extend_schema(
    summary="Update subject (partial)",
    description="Partially update a subject's information. Requires authentication.",
    request=SubjectCreateUpdateSerializer,
    responses={200: SubjectCreateUpdateSerializer},
    tags=["Subjects"]
)

subject_delete_schema = extend_schema(
    summary="Delete subject",
    description="Delete a subject. Requires authentication.",
    responses={204: None},
    tags=["Subjects"]
)


# UserSubject List/Create schemas
user_subject_list_schema = extend_schema(
    summary="List user subjects",
    description="Get a paginated list of subjects for the authenticated user. Supports search and filtering.",
    parameters=[
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search by subject code, name_vi, or name_en"
        ),
        OpenApiParameter(
            name="level",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by user's level (beginner, intermediate, advanced, expert)"
        ),
        OpenApiParameter(
            name="intent",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by intent (learn, teach, both)"
        ),
        OpenApiParameter(
            name="ordering",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Order results by: level, intent, created_at (prefix with - for descending)"
        ),
    ],
    responses={200: UserSubjectListSerializer(many=True)},
    tags=["User Subjects"]
)

user_subject_create_schema = extend_schema(
    summary="Create a user subject",
    description="Add a subject to the authenticated user's learning list. Requires authentication.",
    request=UserSubjectCreateUpdateSerializer,
    responses={201: UserSubjectCreateUpdateSerializer},
    tags=["User Subjects"]
)


# UserSubject Retrieve/Update/Destroy schemas
user_subject_retrieve_schema = extend_schema(
    summary="Get user subject details",
    description="Retrieve detailed information about a specific user subject.",
    responses={200: UserSubjectDetailSerializer},
    tags=["User Subjects"]
)

user_subject_update_schema = extend_schema(
    summary="Update user subject (full)",
    description="Fully update a user subject's information. Requires authentication.",
    request=UserSubjectCreateUpdateSerializer,
    responses={200: UserSubjectCreateUpdateSerializer},
    tags=["User Subjects"]
)

user_subject_partial_update_schema = extend_schema(
    summary="Update user subject (partial)",
    description="Partially update a user subject's information. Requires authentication.",
    request=UserSubjectCreateUpdateSerializer,
    responses={200: UserSubjectCreateUpdateSerializer},
    tags=["User Subjects"]
)

user_subject_delete_schema = extend_schema(
    summary="Delete user subject",
    description="Remove a subject from the authenticated user's learning list. Requires authentication.",
    responses={204: None},
    tags=["User Subjects"]
)


# Goal List/Create schemas
goal_list_schema = extend_schema(
    summary="List goals",
    description="Get a paginated list of goals. Supports search and filtering.",
    parameters=[
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search goals by code or name"
        ),
        OpenApiParameter(
            name="type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter goals by type (daily, weekly, monthly, yearly, milestone)"
        ),
        OpenApiParameter(
            name="ordering",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Order results by: code, name, type, created_at (prefix with - for descending)"
        ),
    ],
    responses={200: GoalListSerializer(many=True)},
    tags=["Goals"]
)

goal_create_schema = extend_schema(
    summary="Create a goal",
    description="Create a new goal. Requires authentication.",
    request=GoalCreateUpdateSerializer,
    responses={201: GoalCreateUpdateSerializer},
    tags=["Goals"]
)


# Goal Retrieve/Update/Destroy schemas
goal_retrieve_schema = extend_schema(
    summary="Get goal details",
    description="Retrieve detailed information about a specific goal including statistics.",
    responses={200: GoalDetailSerializer},
    tags=["Goals"]
)

goal_update_schema = extend_schema(
    summary="Update goal (full)",
    description="Fully update a goal's information. Requires authentication.",
    request=GoalCreateUpdateSerializer,
    responses={200: GoalCreateUpdateSerializer},
    tags=["Goals"]
)

goal_partial_update_schema = extend_schema(
    summary="Update goal (partial)",
    description="Partially update a goal's information. Requires authentication.",
    request=GoalCreateUpdateSerializer,
    responses={200: GoalCreateUpdateSerializer},
    tags=["Goals"]
)

goal_delete_schema = extend_schema(
    summary="Delete goal",
    description="Delete a goal. Requires authentication.",
    responses={204: None},
    tags=["Goals"]
)


# UserGoal List/Create schemas
user_goal_list_schema = extend_schema(
    summary="List user goals",
    description="Get a paginated list of goals for the authenticated user. Supports search and filtering.",
    parameters=[
        OpenApiParameter(
            name="search",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Search by goal code or name"
        ),
        OpenApiParameter(
            name="type",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Filter by goal type (daily, weekly, monthly, yearly, milestone)"
        ),
        OpenApiParameter(
            name="ordering",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Order results by: target_value, target_date, created_at (prefix with - for descending)"
        ),
    ],
    responses={200: UserGoalListSerializer(many=True)},
    tags=["User Goals"]
)

user_goal_create_schema = extend_schema(
    summary="Create a user goal",
    description="Add a goal to the authenticated user's learning goals. Requires authentication.",
    request=UserGoalCreateUpdateSerializer,
    responses={201: UserGoalCreateUpdateSerializer},
    tags=["User Goals"]
)


# UserGoal Retrieve/Update/Destroy schemas
user_goal_retrieve_schema = extend_schema(
    summary="Get user goal details",
    description="Retrieve detailed information about a specific user goal.",
    responses={200: UserGoalDetailSerializer},
    tags=["User Goals"]
)

user_goal_update_schema = extend_schema(
    summary="Update user goal (full)",
    description="Fully update a user goal's information. Requires authentication.",
    request=UserGoalCreateUpdateSerializer,
    responses={200: UserGoalCreateUpdateSerializer},
    tags=["User Goals"]
)

user_goal_partial_update_schema = extend_schema(
    summary="Update user goal (partial)",
    description="Partially update a user goal's information. Requires authentication.",
    request=UserGoalCreateUpdateSerializer,
    responses={200: UserGoalCreateUpdateSerializer},
    tags=["User Goals"]
)

user_goal_delete_schema = extend_schema(
    summary="Delete user goal",
    description="Remove a goal from the authenticated user's learning goals. Requires authentication.",
    responses={204: None},
    tags=["User Goals"]
)
