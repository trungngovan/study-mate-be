from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated

from learning.models import Goal, UserGoal
from learning.serializers import (
    GoalListSerializer,
    GoalDetailSerializer,
    GoalCreateUpdateSerializer,
    UserGoalListSerializer,
    UserGoalDetailSerializer,
    UserGoalCreateUpdateSerializer,
)
from learning.schema import (
    goal_list_schema,
    goal_create_schema,
    goal_retrieve_schema,
    goal_update_schema,
    goal_partial_update_schema,
    goal_delete_schema,
    user_goal_list_schema,
    user_goal_create_schema,
    user_goal_retrieve_schema,
    user_goal_update_schema,
    user_goal_partial_update_schema,
    user_goal_delete_schema,
)


class GoalListCreateAPIView(generics.ListCreateAPIView):
    """
    API view to list all goals or create a new goal.
    
    GET: List all goals with pagination and search (requires authentication)
    POST: Create a new goal (requires authentication)
    """
    queryset = Goal.objects.all().order_by("-created_at")
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["code", "name"]
    ordering_fields = ["code", "name", "type", "created_at"]
    
    @goal_list_schema
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @goal_create_schema
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def get_serializer_class(self):
        """Use different serializers for list and create."""
        if self.request.method == "POST":
            return GoalCreateUpdateSerializer
        return GoalListSerializer
    
    def get_queryset(self):
        """
        Optionally filter goals by type.
        """
        queryset = super().get_queryset()
        
        # Filter by type
        goal_type = self.request.query_params.get("type", None)
        if goal_type:
            queryset = queryset.filter(type=goal_type)
        
        return queryset


class GoalRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update or delete a goal.
    
    GET: Retrieve a single goal by ID (requires authentication)
    PUT/PATCH: Update a goal (requires authentication)
    DELETE: Delete a goal (requires authentication)
    """
    queryset = Goal.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"
    
    @goal_retrieve_schema
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @goal_update_schema
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @goal_partial_update_schema
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @goal_delete_schema
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
    
    def get_serializer_class(self):
        """Use different serializers for retrieve and update."""
        if self.request.method in ["PUT", "PATCH"]:
            return GoalCreateUpdateSerializer
        return GoalDetailSerializer


class UserGoalListCreateAPIView(generics.ListCreateAPIView):
    """
    API view to list all user goals or create a new user goal.
    
    GET: List all user goals for the authenticated user (requires authentication)
    POST: Create a new user goal (requires authentication)
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["goal__code", "goal__name"]
    ordering_fields = ["target_value", "target_date", "created_at"]
    
    @user_goal_list_schema
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @user_goal_create_schema
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def get_serializer_class(self):
        """Use different serializers for list and create."""
        if self.request.method == "POST":
            return UserGoalCreateUpdateSerializer
        return UserGoalListSerializer
    
    def get_queryset(self):
        """
        Return user goals for the authenticated user.
        Optionally filter by goal type.
        """
        queryset = UserGoal.objects.filter(user=self.request.user).select_related("goal").order_by("-created_at")
        
        # Filter by goal type
        goal_type = self.request.query_params.get("type", None)
        if goal_type:
            queryset = queryset.filter(goal__type=goal_type)
        
        return queryset


class UserGoalRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update or delete a user goal.
    
    GET: Retrieve a single user goal by ID (requires authentication)
    PUT/PATCH: Update a user goal (requires authentication)
    DELETE: Delete a user goal (requires authentication)
    """
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"
    
    @user_goal_retrieve_schema
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @user_goal_update_schema
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @user_goal_partial_update_schema
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @user_goal_delete_schema
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
    
    def get_serializer_class(self):
        """Use different serializers for retrieve and update."""
        if self.request.method in ["PUT", "PATCH"]:
            return UserGoalCreateUpdateSerializer
        return UserGoalDetailSerializer
    
    def get_queryset(self):
        """Return user goals for the authenticated user."""
        return UserGoal.objects.filter(user=self.request.user).select_related("goal", "user")
