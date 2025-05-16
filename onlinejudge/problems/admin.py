from django.contrib import admin
from .models import Problem

@admin.register(Problem)  # Decorator syntax
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty', 'author')  # Custom columns
    list_filter = ('difficulty',)  # Adds filter sidebar