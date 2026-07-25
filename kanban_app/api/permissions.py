from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission

from kanban_app.models import Board, Task


class IsBoardOwner(BasePermission):
    message = 'Only the board owner can delete this board.'

    def has_object_permission(self, request, view, obj):
        return obj.owner_id == request.user.id


class IsTaskBoardMember(BasePermission):
    message = 'You must be a board member to modify its tasks.'

    def has_permission(self, request, view):
        if view.action != 'create':
            return True

        board_id = request.data.get('board')
        if board_id is None:
            return True

        board = get_object_or_404(Board, pk=board_id)
        return board.members.filter(pk=request.user.pk).exists()

    def has_object_permission(self, request, view, obj):
        return obj.board.members.filter(pk=request.user.pk).exists()


class IsCommentAuthor(BasePermission):
    message = 'Only the comment author can delete this comment.'

    def has_object_permission(self, request, view, obj):
        return obj.author_id == request.user.id


class IsCommentBoardMember(BasePermission):
    message = 'You must be a board member to access comments.'

    def has_permission(self, request, view):
        task = get_object_or_404(
            Task,
            pk=view.kwargs.get('task_id'),
        )
        return task.board.members.filter(
            pk=request.user.pk
        ).exists()