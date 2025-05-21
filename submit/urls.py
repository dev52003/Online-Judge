from django.urls import path
from submit.views import submit


urlpatterns = [
    path('<int:id>/', submit, name="submit"),
    
]