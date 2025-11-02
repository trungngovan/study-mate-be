"""
Views for groups app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import StudyGroup, GroupMembership, GroupConversation, GroupMessage, GroupMessageRead
from .serializers import (
    StudyGroupListSerializer,
    StudyGroupDetailSerializer,
    CreateStudyGroupSerializer,
    UpdateStudyGroupSerializer,
    GroupMembershipSerializer,
    JoinGroupSerializer,
    InviteUserSerializer,
    UpdateMemberRoleSerializer,
    GroupMessageSerializer,
    CreateGroupMessageSerializer,
    MarkMessagesReadSerializer,
)
from .permissions import (
    IsGroupAdmin,
    IsGroupModerator,
    IsGroupMember,
    IsGroupAdminOrReadOnly,
    CanJoinGroup,
    IsMembershipOwner,
)


User = get_user_model()


class StudyGroupViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing study groups.

    Endpoints:
    - GET /api/groups/ - List study groups
    - POST /api/groups/ - Create a new group
    - GET /api/groups/{id}/ - Get group details
    - PUT/PATCH /api/groups/{id}/ - Update group (admin only)
    - DELETE /api/groups/{id}/ - Delete group (admin only)
    - POST /api/groups/{id}/join/ - Join a group
    - POST /api/groups/{id}/leave/ - Leave a group
    - POST /api/groups/{id}/invite/ - Invite user to group (admin/moderator)
    - GET /api/groups/{id}/members/ - List group members
    - GET /api/groups/my_groups/ - List user's groups
    - GET /api/groups/nearby/ - Find nearby groups
    """

    permission_classes = [IsAuthenticated]
    queryset = StudyGroup.objects.all()

    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'create':
            return CreateStudyGroupSerializer
        elif self.action in ['update', 'partial_update']:
            return UpdateStudyGroupSerializer
        elif self.action == 'retrieve':
            return StudyGroupDetailSerializer
        elif self.action == 'join':
            return JoinGroupSerializer
        elif self.action == 'invite':
            return InviteUserSerializer
        return StudyGroupListSerializer

    def get_permissions(self):
        """Return appropriate permissions based on action."""
        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), IsGroupAdmin()]
        elif self.action == 'destroy':
            return [IsAuthenticated(), IsGroupAdmin()]
        elif self.action == 'invite':
            return [IsAuthenticated(), IsGroupModerator()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Filter queryset based on query parameters.
        """
        user = self.request.user
        queryset = StudyGroup.objects.select_related(
            'created_by', 'school'
        ).prefetch_related(
            'subjects', 'memberships__user'
        )

        # Filter by privacy (exclude invite-only groups user is not a member of)
        if self.action == 'list':
            queryset = queryset.exclude(
                privacy=StudyGroup.PRIVACY_INVITE_ONLY
            ) | queryset.filter(
                memberships__user=user,
                memberships__status=GroupMembership.STATUS_ACTIVE
            )

        # Filter by status
        group_status = self.request.query_params.get('status')
        if group_status:
            queryset = queryset.filter(status=group_status)
        else:
            # By default, only show active groups
            queryset = queryset.filter(status=StudyGroup.STATUS_ACTIVE)

        # Filter by privacy
        privacy = self.request.query_params.get('privacy')
        if privacy:
            queryset = queryset.filter(privacy=privacy)

        # Filter by subject
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            queryset = queryset.filter(subjects__id=subject_id)

        # Filter by school
        school_id = self.request.query_params.get('school')
        if school_id:
            queryset = queryset.filter(school_id=school_id)

        return queryset.distinct().order_by('-created_at')

    @extend_schema(
        request=CreateStudyGroupSerializer,
        responses={201: StudyGroupDetailSerializer},
        description="Create a new study group"
    )
    def create(self, request, *args, **kwargs):
        """Create a new study group."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group = serializer.save()

        response_serializer = StudyGroupDetailSerializer(
            group,
            context={'request': request}
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                enum=['active', 'inactive', 'archived'],
                description='Filter by group status'
            ),
            OpenApiParameter(
                name='privacy',
                type=OpenApiTypes.STR,
                enum=['public', 'private', 'invite_only'],
                description='Filter by privacy setting'
            ),
            OpenApiParameter(
                name='subject',
                type=OpenApiTypes.INT,
                description='Filter by subject ID'
            ),
            OpenApiParameter(
                name='school',
                type=OpenApiTypes.INT,
                description='Filter by school ID'
            ),
        ],
        responses={200: StudyGroupListSerializer(many=True)},
        description="List all study groups with optional filters"
    )
    def list(self, request, *args, **kwargs):
        """List study groups."""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Delete a study group (admin only)"
    )
    def destroy(self, request, *args, **kwargs):
        """Delete (archive) a group."""
        instance = self.get_object()
        instance.status = StudyGroup.STATUS_ARCHIVED
        instance.save(update_fields=['status', 'updated_at'])
        return Response(
            {'message': 'Group archived successfully.'},
            status=status.HTTP_200_OK
        )

    @extend_schema(
        request=JoinGroupSerializer,
        responses={200: GroupMembershipSerializer},
        description="Join or request to join a study group"
    )
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join or request to join a group."""
        group = self.get_object()

        # Check if already a member
        if group.is_member(request.user):
            return Response(
                {'error': 'You are already a member of this group.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if group is full
        if group.is_full:
            return Response(
                {'error': 'This group is full.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check privacy setting
        if group.privacy == StudyGroup.PRIVACY_PUBLIC:
            # Directly join
            membership = GroupMembership.objects.create(
                group=group,
                user=request.user,
                role=GroupMembership.ROLE_MEMBER,
                status=GroupMembership.STATUS_ACTIVE
            )
            message = 'You have joined the group.'
        elif group.privacy == StudyGroup.PRIVACY_PRIVATE:
            # Create pending request
            membership = GroupMembership.objects.create(
                group=group,
                user=request.user,
                role=GroupMembership.ROLE_MEMBER,
                status=GroupMembership.STATUS_PENDING
            )
            message = 'Your request to join has been sent to the group admins.'
        elif group.privacy == StudyGroup.PRIVACY_INVITE_ONLY:
            # Check if user has an invite
            try:
                membership = GroupMembership.objects.get(
                    group=group,
                    user=request.user,
                    status=GroupMembership.STATUS_INVITED
                )
                membership.accept_invitation()
                message = 'You have accepted the invitation and joined the group.'
            except GroupMembership.DoesNotExist:
                return Response(
                    {'error': 'This is an invite-only group. You must be invited to join.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            return Response(
                {'error': 'Invalid privacy setting.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        response_serializer = GroupMembershipSerializer(
            membership,
            context={'request': request}
        )
        return Response(
            {
                'message': message,
                'membership': response_serializer.data
            },
            status=status.HTTP_200_OK
        )

    @extend_schema(
        responses={200: {'message': 'string'}},
        description="Leave a study group"
    )
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a group."""
        group = self.get_object()

        try:
            membership = group.memberships.get(
                user=request.user,
                status=GroupMembership.STATUS_ACTIVE
            )

            # Check if user is the last admin
            if membership.role == GroupMembership.ROLE_ADMIN:
                admin_count = group.memberships.filter(
                    role=GroupMembership.ROLE_ADMIN,
                    status=GroupMembership.STATUS_ACTIVE
                ).count()

                if admin_count == 1:
                    return Response(
                        {'error': 'You are the last admin. Please promote another member to admin before leaving.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            membership.leave()
            return Response(
                {'message': 'You have left the group.'},
                status=status.HTTP_200_OK
            )
        except GroupMembership.DoesNotExist:
            return Response(
                {'error': 'You are not a member of this group.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        request=InviteUserSerializer,
        responses={200: GroupMembershipSerializer},
        description="Invite a user to join the group (admin/moderator only)"
    )
    @action(detail=True, methods=['post'])
    def invite(self, request, pk=None):
        """Invite a user to the group."""
        group = self.get_object()
        serializer = InviteUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_to_invite = get_object_or_404(User, pk=serializer.validated_data['user_id'])

        # Check if user is already a member
        if group.is_member(user_to_invite):
            return Response(
                {'error': 'User is already a member of this group.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if invitation already exists
        existing_invite = group.memberships.filter(
            user=user_to_invite,
            status__in=[GroupMembership.STATUS_INVITED, GroupMembership.STATUS_PENDING]
        ).first()

        if existing_invite:
            return Response(
                {'error': 'User already has a pending invitation or request.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create invitation
        membership = GroupMembership.objects.create(
            group=group,
            user=user_to_invite,
            role=GroupMembership.ROLE_MEMBER,
            status=GroupMembership.STATUS_INVITED,
            invited_by=request.user
        )

        response_serializer = GroupMembershipSerializer(
            membership,
            context={'request': request}
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                description='Page number for pagination (default: 1)'
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                description='Number of results per page (default: 12, max: 100)'
            ),
        ],
        responses={200: GroupMembershipSerializer(many=True)},
        description="List all members of the group (paginated)"
    )
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """List group members with pagination."""
        from rest_framework.pagination import PageNumberPagination
        
        group = self.get_object()

        # Only show active members to non-members
        if not group.is_member(request.user):
            memberships = group.memberships.filter(status=GroupMembership.STATUS_ACTIVE)
        else:
            # Show all memberships to members (including pending)
            memberships = group.memberships.all()

        memberships = memberships.select_related('user', 'invited_by').order_by('-role', 'joined_at')

        # Create paginator instance
        paginator = PageNumberPagination()
        
        # Get page_size from query params, default to 12
        try:
            page_size = int(request.query_params.get('page_size', 12))
            # Limit max page_size
            if page_size > 100:
                page_size = 100
            paginator.page_size = page_size
        except (ValueError, TypeError):
            paginator.page_size = 12
        
        paginator.max_page_size = 100
        
        # Convert queryset to list to ensure pagination works
        memberships_list = list(memberships)
        total_count = len(memberships_list)
        
        # Get page number from query params (default: 1)
        try:
            page_number = int(request.query_params.get('page', 1))
        except (ValueError, TypeError):
            page_number = 1
        
        # Calculate pagination
        start_index = (page_number - 1) * paginator.page_size
        end_index = start_index + paginator.page_size
        paginated_memberships = memberships_list[start_index:end_index]
        
        # Serialize the paginated results
        serializer = GroupMembershipSerializer(
            paginated_memberships,
            many=True,
            context={'request': request}
        )
        
        # Create paginated response manually
        response_data = {
            'count': total_count,
            'next': None,
            'previous': None,
            'results': serializer.data
        }
        
        # Set next URL if there are more results
        if end_index < total_count:
            next_page = page_number + 1
            from urllib.parse import urlencode, urlparse, urlunparse, parse_qs
            parsed = urlparse(request.build_absolute_uri())
            query_params = parse_qs(parsed.query)
            query_params['page'] = [str(next_page)]
            query_params['page_size'] = [str(paginator.page_size)]
            new_query = urlencode(query_params, doseq=True)
            response_data['next'] = urlunparse(parsed._replace(query=new_query))
        
        # Set previous URL if not on first page
        if page_number > 1:
            prev_page = page_number - 1
            from urllib.parse import urlencode, urlparse, urlunparse, parse_qs
            parsed = urlparse(request.build_absolute_uri())
            query_params = parse_qs(parsed.query)
            query_params['page'] = [str(prev_page)]
            query_params['page_size'] = [str(paginator.page_size)]
            new_query = urlencode(query_params, doseq=True)
            response_data['previous'] = urlunparse(parsed._replace(query=new_query))
        
        return Response(response_data)

    @extend_schema(
        responses={200: StudyGroupListSerializer(many=True)},
        description="List groups the current user is a member of"
    )
    @action(detail=False, methods=['get'])
    def my_groups(self, request):
        """List user's groups."""
        user = request.user

        queryset = StudyGroup.objects.filter(
            memberships__user=user,
            memberships__status=GroupMembership.STATUS_ACTIVE
        ).select_related('created_by', 'school').prefetch_related(
            'subjects', 'memberships__user'
        ).order_by('-created_at')

        serializer = StudyGroupListSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='radius_km',
                type=OpenApiTypes.FLOAT,
                description='Search radius in kilometers (default: 10km)'
            ),
            OpenApiParameter(
                name='subject',
                type=OpenApiTypes.INT,
                description='Filter by subject ID'
            ),
        ],
        responses={200: StudyGroupListSerializer(many=True)},
        description="Find nearby study groups"
    )
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """Find nearby study groups."""
        user = request.user

        if not user.geom_last_point:
            return Response(
                {'error': 'You must set your location first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get radius from query params (default 10km)
        radius_km = float(request.query_params.get('radius_km', 10))

        # Filter groups with location
        queryset = StudyGroup.objects.filter(
            geom_point__isnull=False,
            status=StudyGroup.STATUS_ACTIVE
        ).exclude(
            privacy=StudyGroup.PRIVACY_INVITE_ONLY
        ).filter(
            geom_point__dwithin=(user.geom_last_point, D(km=radius_km))
        ).annotate(
            distance_km=Distance('geom_point', user.geom_last_point)
        ).select_related('created_by', 'school').prefetch_related(
            'subjects'
        ).order_by('distance_km')

        # Apply subject filter if provided
        subject_id = request.query_params.get('subject')
        if subject_id:
            queryset = queryset.filter(subjects__id=subject_id)

        serializer = StudyGroupListSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class GroupMembershipViewSet(viewsets.GenericViewSet):
    """
    ViewSet for managing group memberships.

    Endpoints:
    - GET /api/groups/memberships/{id}/ - Get membership details
    - PATCH /api/groups/memberships/{id}/role/ - Update member role (admin only)
    - POST /api/groups/memberships/{id}/accept/ - Accept join request (admin only)
    - POST /api/groups/memberships/{id}/reject/ - Reject join request (admin only)
    - POST /api/groups/memberships/{id}/remove/ - Remove member (admin only)
    """

    permission_classes = [IsAuthenticated]
    queryset = GroupMembership.objects.all()
    serializer_class = GroupMembershipSerializer

    def get_queryset(self):
        """Filter to memberships the user can see."""
        user = self.request.user
        return GroupMembership.objects.filter(
            models.Q(group__memberships__user=user, group__memberships__status=GroupMembership.STATUS_ACTIVE) |
            models.Q(user=user)
        ).select_related('group', 'user', 'invited_by').distinct()

    @extend_schema(
        responses={200: GroupMembershipSerializer},
        description="Get membership details"
    )
    def retrieve(self, request, pk=None):
        """Get membership details."""
        membership = self.get_object()
        serializer = self.get_serializer(membership)
        return Response(serializer.data)

    @extend_schema(
        request=UpdateMemberRoleSerializer,
        responses={200: GroupMembershipSerializer},
        description="Update a member's role (admin only)"
    )
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsGroupAdmin])
    def role(self, request, pk=None):
        """Update member role (admin only)."""
        membership = self.get_object()

        serializer = UpdateMemberRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_role = serializer.validated_data['role']

        # Check if trying to demote the last admin
        if membership.role == GroupMembership.ROLE_ADMIN and new_role != GroupMembership.ROLE_ADMIN:
            admin_count = membership.group.memberships.filter(
                role=GroupMembership.ROLE_ADMIN,
                status=GroupMembership.STATUS_ACTIVE
            ).count()

            if admin_count == 1:
                return Response(
                    {'error': 'Cannot demote the last admin. Promote another member first.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        membership.role = new_role
        membership.save(update_fields=['role', 'updated_at'])

        response_serializer = GroupMembershipSerializer(
            membership,
            context={'request': request}
        )
        return Response(response_serializer.data)

    @extend_schema(
        responses={200: GroupMembershipSerializer},
        description="Accept a join request (admin only)"
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsGroupAdmin])
    def accept(self, request, pk=None):
        """Accept a join request."""
        membership = self.get_object()

        if membership.status != GroupMembership.STATUS_PENDING:
            return Response(
                {'error': 'This membership is not pending.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        membership.accept_request()

        response_serializer = GroupMembershipSerializer(
            membership,
            context={'request': request}
        )
        return Response(response_serializer.data)

    @extend_schema(
        responses={200: {'message': 'string'}},
        description="Reject a join request (admin only)"
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsGroupAdmin])
    def reject(self, request, pk=None):
        """Reject a join request."""
        membership = self.get_object()

        if membership.status != GroupMembership.STATUS_PENDING:
            return Response(
                {'error': 'This membership is not pending.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        membership.delete()
        return Response({'message': 'Join request rejected.'})

    @extend_schema(
        responses={200: {'message': 'string'}},
        description="Remove a member from the group (admin only)"
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsGroupAdmin])
    def remove(self, request, pk=None):
        """Remove a member from the group."""
        membership = self.get_object()

        # Check if trying to remove the last admin
        if membership.role == GroupMembership.ROLE_ADMIN:
            admin_count = membership.group.memberships.filter(
                role=GroupMembership.ROLE_ADMIN,
                status=GroupMembership.STATUS_ACTIVE
            ).count()

            if admin_count == 1:
                return Response(
                    {'error': 'Cannot remove the last admin.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        membership.remove()
        return Response({'message': 'Member removed from group.'})


class GroupMessageViewSet(viewsets.GenericViewSet):
    """
    ViewSet for managing group messages.

    Endpoints:
    - GET /api/groups/{group_id}/messages/ - List messages (paginated)
    - POST /api/groups/{group_id}/messages/ - Send a message
    - POST /api/groups/{group_id}/messages/mark_read/ - Mark messages as read
    """

    permission_classes = [IsAuthenticated, IsGroupMember]
    serializer_class = GroupMessageSerializer
    pagination_class = None  # We'll use custom pagination

    def get_group(self):
        """Get the group from the URL."""
        group_id = self.kwargs.get('group_id')
        return get_object_or_404(StudyGroup, pk=group_id)

    def get_queryset(self):
        """Get messages for the group."""
        group = self.get_group()

        # Ensure user is a member
        if not group.is_member(self.request.user):
            return GroupMessage.objects.none()

        try:
            conversation = group.conversation
            # Order by -created_at for pagination (newest first)
            # Frontend will reverse to show oldest first
            return GroupMessage.objects.filter(
                conversation=conversation
            ).select_related('sender').order_by('-created_at')
        except GroupConversation.DoesNotExist:
            return GroupMessage.objects.none()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                description='Page number'
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                description='Number of messages per page (default: 50)'
            ),
        ],
        responses={200: GroupMessageSerializer(many=True)},
        description="List group messages with pagination"
    )
    def list(self, request, group_id=None):
        """List group messages with pagination."""
        from rest_framework.pagination import PageNumberPagination
        
        queryset = self.get_queryset()
        
        # Custom paginator
        paginator = PageNumberPagination()
        paginator.page_size = int(request.query_params.get('page_size', 50))
        paginator.max_page_size = 100
        
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=CreateGroupMessageSerializer,
        responses={201: GroupMessageSerializer},
        description="Send a message to the group"
    )
    def create(self, request, group_id=None):
        """Send a message to the group."""
        group = self.get_group()

        # Ensure user is a member
        if not group.is_member(request.user):
            return Response(
                {'error': 'You must be a member to send messages.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get or create conversation
        conversation, created = GroupConversation.objects.get_or_create(group=group)

        serializer = CreateGroupMessageSerializer(
            data=request.data,
            context={'request': request, 'conversation': conversation}
        )
        serializer.is_valid(raise_exception=True)
        message = serializer.save()

        response_serializer = GroupMessageSerializer(
            message,
            context={'request': request}
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=MarkMessagesReadSerializer,
        responses={200: {'message': 'string'}},
        description="Mark messages as read"
    )
    @action(detail=False, methods=['post'])
    def mark_read(self, request, group_id=None):
        """Mark messages as read."""
        group = self.get_group()

        if not group.is_member(request.user):
            return Response(
                {'error': 'You must be a member to mark messages as read.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = MarkMessagesReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message_ids = serializer.validated_data['message_ids']

        # Bulk create read records
        read_records = []
        for message_id in message_ids:
            if not GroupMessageRead.objects.filter(message_id=message_id, user=request.user).exists():
                read_records.append(
                    GroupMessageRead(message_id=message_id, user=request.user)
                )

        GroupMessageRead.objects.bulk_create(read_records, ignore_conflicts=True)

        return Response({'message': f'{len(read_records)} messages marked as read.'})
