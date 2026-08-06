from django.db.models import Count, Prefetch, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from kanban_app.api.permissions import (
    IsBoardMemberOrOwner,
    IsBoardOwner,
    IsCommentAuthor,
    IsCommentBoardMember,
    IsTaskCreatorOrBoardOwner,
    IsTaskBoardMember,
)
from kanban_app.api.serializers import (
    BoardCreateSerializer,
    BoardDetailSerializer,
    BoardListSerializer,
    BoardUpdateSerializer,
    CommentSerializer,
    TaskCreateSerializer,
    TaskSerializer,
    TaskUpdateSerializer,
    TaskUpdateResponseSerializer,
)
from kanban_app.models import Board, Comment, Task


def get_board_annotations():
    to_do = Q(tasks__status=Task.StatusChoices.TO_DO)
    high_priority = Q(tasks__priority=Task.PriorityChoices.HIGH)

    return {
        'member_count': Count('members', distinct=True),
        'ticket_count': Count('tasks', distinct=True),
        'tasks_to_do_count': Count(
            'tasks', filter=to_do, distinct=True,
        ),
        'tasks_high_prio_count': Count(
            'tasks', filter=high_priority, distinct=True,
        ),
    }


def get_accessible_boards(user):
    return (
        Board.objects
        .annotate(**get_board_annotations())
        .filter(Q(owner=user) | Q(members=user))
        .distinct()
    )


def get_board_tasks_queryset():
    return (
        Task.objects
        .select_related('assignee', 'reviewer')
        .annotate(comments_count=Count('comments'))
    )


class BoardViewSet(viewsets.ModelViewSet):
    serializer_class = BoardListSerializer
    http_method_names = [
        'get',
        'post',
        'patch',
        'delete',
        'head',
        'options',
    ]
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated(), IsBoardOwner()]

        if self.action in ('retrieve', 'partial_update'):
            return [IsAuthenticated(), IsBoardMemberOrOwner()]

        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return BoardCreateSerializer

        if self.action == 'retrieve':
            return BoardDetailSerializer

        if self.action == 'partial_update':
            return BoardUpdateSerializer

        return BoardListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        board = self.get_queryset().get(pk=serializer.instance.pk)
        response_serializer = BoardListSerializer(board)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        # The ``list`` action is scoped to boards the user can access. Detail
        # actions query across all boards so that object-level permissions can
        # return ``403`` for an existing board the user may not access, while a
        # missing board still returns ``404``.
        if self.action == 'list':
            return get_accessible_boards(self.request.user)

        queryset = Board.objects.annotate(**get_board_annotations())
        if self.action != 'retrieve':
            return queryset

        tasks = Prefetch(
            'tasks',
            queryset=get_board_tasks_queryset(),
        )
        return queryset.prefetch_related(tasks)


class TaskViewSet(viewsets.ModelViewSet):
    """CRUD endpoints for tasks plus ``assigned-to-me`` and ``reviewing``.

    Board members may create, view and update tasks; only the task creator or
    the board owner may delete a task.
    """

    serializer_class = TaskSerializer
    http_method_names = [
        'get',
        'post',
        'patch',
        'delete',
        'head',
        'options',
    ]
    permission_classes = [
        IsAuthenticated,
        IsTaskBoardMember,
    ]

    def get_permissions(self):
        if self.action == 'destroy':
            return [
                IsAuthenticated(),
                IsTaskCreatorOrBoardOwner(),
            ]

        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer

        if self.action == 'partial_update':
            return TaskUpdateSerializer

        return TaskSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        task = self.get_queryset().get(pk=serializer.instance.pk)
        response_serializer = TaskSerializer(task)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = self.get_serializer(
            task,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        task = self.get_queryset().get(pk=task.pk)
        response_serializer = TaskUpdateResponseSerializer(task)
        return Response(response_serializer.data)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(
        detail=False,
        methods=['get'],
        url_path='assigned-to-me',
    )
    def assigned_to_me(self, request):
        """Return the tasks assigned to the current user."""
        tasks = self.get_queryset().filter(
            assignee=request.user
        )
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        url_path='reviewing',
    )
    def reviewing(self, request):
        tasks = self.get_queryset().filter(
            reviewer=self.request.user
        )
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = (
            Task.objects
            .select_related('assignee', 'reviewer')
            .annotate(comments_count=Count('comments'))
        )

        if self.action == 'list':
            return queryset.filter(
                board__members=self.request.user
            )

        return queryset


class CommentViewSet(viewsets.ModelViewSet):
    """List, create and delete comments on a given task.

    Any member of the task's board may read and add comments; only the comment
    author may delete their own comment.
    """

    serializer_class = CommentSerializer
    http_method_names = [
        'get',
        'post',
        'delete',
    ]

    def get_permissions(self):
        if self.action == 'destroy':
            return [
                IsAuthenticated(),
                IsCommentAuthor(),
            ]

        return [
            IsAuthenticated(),
            IsCommentBoardMember(),
        ]

    def perform_create(self, serializer):
        serializer.save(
            task_id=self.kwargs.get('task_id'),
            author=self.request.user,
        )

    def get_queryset(self):
        return (
            Comment.objects
            .filter(task_id=self.kwargs.get('task_id'))
            .select_related('author')
        )
