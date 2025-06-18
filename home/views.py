from django.shortcuts import render

def home(request):
    # Add any context data you want to pass to the template
    context = {
        'recent_problems': []  # You'll replace this with actual query later
    }
    return render(request, 'home/home.html', context)