from django.urls import path
from .views import ProblemListView

urlpatterns = [
    path('problems/', ProblemListView.as_view(), name='problem_list'),
]