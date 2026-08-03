from django.contrib.auth.models import User
from rest_framework import serializers

from auth_app.api.serializers import UserSummarySerializer
from kanban_app.models import Board, Comment, Task


class BoardListSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(read_only=True)
    ticket_count = serializers.IntegerField(read_only=True)
    tasks_to_do_count = serializers.IntegerField(read_only=True)
    tasks_high_prio_count = serializers.IntegerField(read_only=True)
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'tasks_high_prio_count',
            'owner_id',
        ]


class BoardCreateSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = Board
        fields = [
            'title',
            'members',
        ]


class BoardUpdateSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )
    owner_data = UserSummarySerializer(
        source='owner',
        read_only=True,
    )
    members_data = UserSummarySerializer(
        source='members',
        many=True,
        read_only=True,
    )

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'owner_data',
            'members',
            'members_data',
        ]


class TaskCreateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        source='assignee',
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source='reviewer',
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )

    class Meta:
        model = Task
        fields = [
            'board',
            'title',
            'description',
            'status',
            'priority',
            'assignee_id',
            'reviewer_id',
            'due_date',
        ]

    def validate(self, attrs):
        board = attrs['board']
        member_ids = set(
            board.members.values_list('id', flat=True)
        )

        for role in ('assignee', 'reviewer'):
            user = attrs.get(role)

            if user and user.id not in member_ids:
                raise serializers.ValidationError({
                    f'{role}_id': 'User must be a board member.',
                })
        return attrs


class TaskUpdateSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        source='assignee',
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        source='reviewer',
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )

    class Meta:
        model = Task
        fields = [
            'title',
            'description',
            'status',
            'priority',
            'assignee_id',
            'reviewer_id',
            'due_date',
        ]

    def validate(self, attrs):
        board = self.instance.board
        member_ids = set(
            board.members.values_list('id', flat=True)
        )
        for role in ('assignee', 'reviewer'):
            user = attrs.get(role)
            if user and user.id not in member_ids:
                raise serializers.ValidationError({
                    f'{role}_id': 'User must be a board member.',
                })
        return attrs


class TaskSerializer(serializers.ModelSerializer):
    assignee = UserSummarySerializer(read_only=True)
    reviewer = UserSummarySerializer(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'board',
            'title',
            'description',
            'status',
            'priority',
            'assignee',
            'reviewer',
            'due_date',
            'comments_count',
        ]


class BoardTaskSerializer(TaskSerializer):
    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'status',
            'priority',
            'assignee',
            'reviewer',
            'due_date',
            'comments_count',
        ]


class TaskUpdateResponseSerializer(serializers.ModelSerializer):
    assignee = UserSummarySerializer(read_only=True)
    reviewer = UserSummarySerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'status',
            'priority',
            'assignee',
            'reviewer',
            'due_date',
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(
        source='author.first_name',
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = [
            'id',
            'created_at',
            'author',
            'content',
        ]


class BoardDetailSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(
        source='owner.id',
        read_only=True,
    )
    members = UserSummarySerializer(
        many=True,
        read_only=True,
    )
    tasks = BoardTaskSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'owner_id',
            'members',
            'tasks',
        ]
