from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Problem(models.Model):
    DIFFICULTY_CHOICES = [
        ('E', 'Easy'),
        ('M', 'Medium'),
        ('H', 'Hard'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=1, choices=DIFFICULTY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    time_limit = models.IntegerField(default=1)  # in seconds
    memory_limit = models.IntegerField(default=256)  # in MB
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} ({self.get_difficulty_display()})"