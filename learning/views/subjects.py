from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated

from learning.models import Subject, UserSubject
from learning.serializers import (
    SubjectListSerializer,
    SubjectDetailSerializer,
    SubjectCreateUpdateSerializer,
    UserSubjectListSerializer,
    UserSubjectDetailSerializer,
    UserSubjectCreateUpdateSerializer,
)
from learning.schema import (
    subject_list_schema,
    subject_create_schema,
    subject_retrieve_schema,
    subject_update_schema,
    subject_partial_update_schema,
    subject_delete_schema,
    user_subject_list_schema,
    user_subject_create_schema,
    user_subject_retrieve_schema,
    user_subject_update_schema,
    user_subject_partial_update_schema,
    user_subject_delete_schema,
)


class SubjectListCreateAPIView(generics.ListCreateAPIView):
    """
    API view to list all subjects or create a new subject.
    
    GET: List all subjects with pagination and search (requires authentication)
    POST: Create a new subject (requires authentication)
    """
    queryset = Subject.objects.all().order_by("-created_at")
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["code", "name_vi", "name_en"]
    ordering_fields = ["code", "name_en", "created_at"]
    
    @subject_list_schema
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @subject_create_schema
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def get_serializer_class(self):
        """Use different serializers for list and create."""
        if self.request.method == "POST":
            return SubjectCreateUpdateSerializer
        return SubjectListSerializer
    
    def get_queryset(self):
        """
        Optionally filter subjects by level.
        """
        queryset = super().get_queryset()
        
        # Filter by level
        level = self.request.query_params.get("level", None)
        if level:
            queryset = queryset.filter(level=level)
        
        return queryset


class SubjectRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update or delete a subject.
    
    GET: Retrieve a single subject by ID (requires authentication)
    PUT/PATCH: Update a subject (requires authentication)
    DELETE: Delete a subject (requires authentication)
    """
    queryset = Subject.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"
    
    @subject_retrieve_schema
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @subject_update_schema
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @subject_partial_update_schema
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @subject_delete_schema
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
    
    def get_serializer_class(self):
        """Use different serializers for retrieve and update."""
        if self.request.method in ["PUT", "PATCH"]:
            return SubjectCreateUpdateSerializer
        return SubjectDetailSerializer


class UserSubjectListCreateAPIView(generics.ListCreateAPIView):
    """
    API view to list all user subjects or create a new user subject.
    
    GET: List all user subjects for the authenticated user (requires authentication)
    POST: Create a new user subject (requires authentication)
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["subject__code", "subject__name_vi", "subject__name_en"]
    ordering_fields = ["level", "intent", "created_at"]
    
    @user_subject_list_schema
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @user_subject_create_schema
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def get_serializer_class(self):
        """Use different serializers for list and create."""
        if self.request.method == "POST":
            return UserSubjectCreateUpdateSerializer
        return UserSubjectListSerializer
    
    def get_queryset(self):
        """
        Return user subjects for the authenticated user.
        Optionally filter by level or intent.
        """
        queryset = UserSubject.objects.filter(user=self.request.user).select_related("subject").order_by("-created_at")
        
        # Filter by level
        level = self.request.query_params.get("level", None)
        if level:
            queryset = queryset.filter(level=level)
        
        # Filter by intent
        intent = self.request.query_params.get("intent", None)
        if intent:
            queryset = queryset.filter(intent=intent)
        
        return queryset


class UserSubjectRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update or delete a user subject.
    
    GET: Retrieve a single user subject by ID (requires authentication)
    PUT/PATCH: Update a user subject (requires authentication)
    DELETE: Delete a user subject (requires authentication)
    """
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"
    
    @user_subject_retrieve_schema
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @user_subject_update_schema
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @user_subject_partial_update_schema
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @user_subject_delete_schema
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
    
    def get_serializer_class(self):
        """Use different serializers for retrieve and update."""
        if self.request.method in ["PUT", "PATCH"]:
            return UserSubjectCreateUpdateSerializer
        return UserSubjectDetailSerializer
    
    def get_queryset(self):
        """Return user subjects for the authenticated user."""
        return UserSubject.objects.filter(user=self.request.user).select_related("subject", "user")
