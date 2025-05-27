# from django.contrib import admin
# from problems.models import Problem

# # Register your models here.
# admin.site.register(Problem)
from django.contrib import admin
from .models import Problem, TestCase

class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 1

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    inlines = [TestCaseInline]
