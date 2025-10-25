from .subjects import (
    SubjectListCreateAPIView,
    SubjectRetrieveUpdateDestroyAPIView,
    UserSubjectListCreateAPIView,
    UserSubjectRetrieveUpdateDestroyAPIView,
)
from .goals import (
    GoalListCreateAPIView,
    GoalRetrieveUpdateDestroyAPIView,
    UserGoalListCreateAPIView,
    UserGoalRetrieveUpdateDestroyAPIView,
)

__all__ = [
    # Subject views
    "SubjectListCreateAPIView",
    "SubjectRetrieveUpdateDestroyAPIView",
    # UserSubject views
    "UserSubjectListCreateAPIView",
    "UserSubjectRetrieveUpdateDestroyAPIView",
    # Goal views
    "GoalListCreateAPIView",
    "GoalRetrieveUpdateDestroyAPIView",
    # UserGoal views
    "UserGoalListCreateAPIView",
    "UserGoalRetrieveUpdateDestroyAPIView",
]
