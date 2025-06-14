from django.db import models
from django.contrib.auth.models import User
from problems.models import Problem

class CodeSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    language = models.CharField(max_length=100)
    code = models.TextField()
    input_data = models.TextField(null=True, blank=True)
    expected_output = models.TextField(null=True, blank=True)
    output_data = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    verdict = models.CharField(max_length=50, null=True)
    ai_review = models.TextField(null=True, blank=True)  

    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} - {self.language}"