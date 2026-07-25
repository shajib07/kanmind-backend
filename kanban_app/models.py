from django.contrib.auth.models import User
from django.db import models

class Board(models.Model):
    objects = models.Manager()

    title = models.CharField(max_length=255)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_boards'
    )

    members = models.ManyToManyField(
        User,
        related_name='boards',
        blank=True,
    )

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Task(models.Model):
    objects = models.Manager()

    class StatusChoices(models.TextChoices):
        TO_DO = 'to-do', 'To do'
        IN_PROGRESS = 'in-progress', 'In progress'
        REVIEW = 'review', 'Review'
        DONE = 'done', 'Done'

    class PriorityChoices(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'

    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='tasks',
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.TO_DO,
    )
    priority = models.CharField(
        max_length=20,
        choices=PriorityChoices.choices,
        default=PriorityChoices.MEDIUM,
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='assigned_tasks',
        null=True,
        blank=True,
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='review_tasks',
        null=True,
        blank=True,
    )
    due_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='created_tasks',
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['due_date', 'title']

    def __str__(self):
        return self.title


class Comment(models.Model):
    objects = models.Manager()

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author} on {self.task}'
