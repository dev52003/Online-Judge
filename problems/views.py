from django.shortcuts import render
from problems.models import Problem
from submit.forms import CodeSubmissionForm
from submit.views import submit
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


def problems_list(request):
    difficulty = request.GET.get('difficulty')  # Get the difficulty from the URL
    if difficulty in ['Easy', 'Medium', 'Hard']:
        problems = Problem.objects.filter(difficulty=difficulty)
    else:
        problems = Problem.objects.all()  # Default to showing all problems
    return render(request, 'problems_list1.html', {'problems': problems})


def problem_details(request, id):
    problems = Problem.objects.get(id=id)
    output = None  # To store code output
    if request.method == 'POST':
        form = CodeSubmissionForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            language = form.cleaned_data['language']
            output = submit(code, language)  # Use the submit function to run the code
    else:
        form = CodeSubmissionForm()

    context = {
        'problems': problems,
        'form': form,
        'output': output,  # Pass output to the template
    }
    return render(request, 'submit/cp.html', context)
