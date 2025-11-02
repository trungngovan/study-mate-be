"""
Views for dashboard statistics.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .serializers import DashboardStatisticsSerializer
from .services import SessionStatisticsService
from matching.services import ConnectionService


@extend_schema(
    summary="Get dashboard statistics",
    description="""
    Retrieve comprehensive dashboard statistics for the authenticated user.
    
    Includes:
    - Session statistics (hosting, attending, participation details)
    - Connection statistics (pending requests, accepted connections)
    """,
    responses={
        200: DashboardStatisticsSerializer,
        401: {
            "type": "object",
            "properties": {
                "detail": {"type": "string", "example": "Authentication credentials were not provided."}
            }
        }
    },
    tags=["Dashboard"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_statistics(request):
    """
    Get dashboard statistics for the authenticated user.
    
    Returns aggregated statistics including:
    - Session statistics (hosting, attending, participation)
    - Connection statistics (requests, connections)
    """
    # Get session statistics
    session_service = SessionStatisticsService(request.user)
    session_stats = session_service.get_statistics()
    
    # Get connection statistics using existing ConnectionService
    connection_stats = ConnectionService.get_connection_statistics(request.user)
    
    # Combine statistics
    stats = {
        'sessions': session_stats,
        'connections': connection_stats,
    }
    
    serializer = DashboardStatisticsSerializer(stats)
    return Response(serializer.data, status=status.HTTP_200_OK)

