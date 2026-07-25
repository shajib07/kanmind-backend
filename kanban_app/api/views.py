from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from kanban_app.api.permissions import (
    IsBoardOwner,
    IsCommentAuthor,
    IsCommentBoardMember,
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
)
from kanban_app.models import Board, Comment, Task


class BoardViewSet(viewsets.ModelViewSet):
    serializer_class = BoardListSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated(), IsBoardOwner()]

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
        return (
            Board.objects
            .annotate(
                member_count=Count(
                    'members',
                    distinct=True,
                ),
                ticket_count=Count(
                    'tasks',
                    distinct=True,
                ),
                tasks_to_do_count=Count(
                    'tasks',
                    filter=Q(
                        tasks__status=Task.StatusChoices.TO_DO,
                    ),
                    distinct=True,
                ),
                tasks_high_prio_count=Count(
                    'tasks',
                    filter=Q(
                        tasks__priority=Task.PriorityChoices.HIGH,
                    ),
                    distinct=True,
                ),
            )
            .filter(
                Q(owner=self.request.user)
                | Q(members=self.request.user)
            )
            .distinct()
        )


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [
        IsAuthenticated,
        IsTaskBoardMember,
    ]

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
        response_serializer = TaskSerializer(task)
        return Response(response_serializer.data)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(
        detail=False,
        methods=['get'],
        url_path='assigned-to-me',
    )
    def assigned_to_me(self, request):
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
        return (
            Task.objects
            .select_related('assignee', 'reviewer')
            .annotate(comments_count=Count('comments'))
        )


class CommentViewSet(viewsets.ModelViewSet):
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
