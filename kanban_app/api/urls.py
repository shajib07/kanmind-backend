from rest_framework.routers import DefaultRouter
from django.urls import path

from kanban_app.api.views import (
    BoardViewSet,
    CommentViewSet,
    TaskViewSet,
)

router = DefaultRouter()
router.register('boards', BoardViewSet, basename='board')
router.register('tasks', TaskViewSet, basename='task')

comment_list = CommentViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

comment_detail = CommentViewSet.as_view({
    'delete': 'destroy',
})

urlpatterns = [
    path(
        'tasks/<int:task_id>/comments/',
        comment_list,
        name='task-comment-list',
    ),
    path(
        'tasks/<int:task_id>/comments/<int:pk>/',
        comment_detail,
        name='task-comment-detail',
    ),
]

urlpatterns += router.urls
