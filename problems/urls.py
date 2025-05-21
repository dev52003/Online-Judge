from django.urls import path
from problems.views import problems_list,problem_details
from submit.views import submit

urlpatterns = [
    path('all/', problems_list, name='problems-list'),
   # path('<int:id>/', problem_details, name = 'problem-details'),
    path('<int:id>/', submit, name = 'problem-details'),
]