from django.urls import path
from learning.views import (
    SubjectListCreateAPIView,
    SubjectRetrieveUpdateDestroyAPIView,
    UserSubjectListCreateAPIView,
    UserSubjectRetrieveUpdateDestroyAPIView,
    GoalListCreateAPIView,
    GoalRetrieveUpdateDestroyAPIView,
    UserGoalListCreateAPIView,
    UserGoalRetrieveUpdateDestroyAPIView,
)

app_name = "learning"

urlpatterns = [
    # Subject endpoints
    path("subjects/", SubjectListCreateAPIView.as_view(), name="subject-list-create"),
    path("subjects/<int:pk>/", SubjectRetrieveUpdateDestroyAPIView.as_view(), name="subject-detail"),
    
    # User Subject endpoints
    path("user-subjects/", UserSubjectListCreateAPIView.as_view(), name="user-subject-list-create"),
    path("user-subjects/<int:pk>/", UserSubjectRetrieveUpdateDestroyAPIView.as_view(), name="user-subject-detail"),
    
    # Goal endpoints
    path("goals/", GoalListCreateAPIView.as_view(), name="goal-list-create"),
    path("goals/<int:pk>/", GoalRetrieveUpdateDestroyAPIView.as_view(), name="goal-detail"),
    
    # User Goal endpoints
    path("user-goals/", UserGoalListCreateAPIView.as_view(), name="user-goal-list-create"),
    path("user-goals/<int:pk>/", UserGoalRetrieveUpdateDestroyAPIView.as_view(), name="user-goal-detail"),
]
