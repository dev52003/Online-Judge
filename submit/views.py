from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from submit.forms import CodeSubmissionForm
from django.conf import settings
from problems.models import Problem
import uuid
import subprocess
from pathlib import Path
import os
import google.generativeai as genai
from django.core.exceptions import ImproperlyConfigured
from django.core.cache import cache

# Configure Gemini AI
try:
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
except:
    pass

def get_ai_review(code, language, problem_description=None):
    """Get AI code review from Gemini with error handling"""
    if not os.getenv('GEMINI_API_KEY'):
        return "AI review unavailable (API key not configured)"
    
    try:
        # Updated model name to gemini-1.0-pro
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""Provide a concise code review for this {language} submission:
        1. Identify 2-3 key strengths
        2. Suggest 2-3 specific improvements
        3. Note any potential bugs
        4. Comment on code style/readability
        5. Keep it under 100 words
        6. Give in clear points
        
        Problem Context: {problem_description or 'Not provided'}
        
        Code:
        {code}
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        # More specific error handling
        if "404" in str(e) and "models/gemini-pro" in str(e):
            return "AI review unavailable: Please update the model name in server configuration"
        return f"AI review unavailable: {str(e)}"
    
def submit(request, id):
    if request.method == "POST":
        form = CodeSubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            problem = Problem.objects.get(id=id)
            action = request.POST.get("action", "submit")
            custom_input = request.POST.get("custom_input", None)

            # Handle custom test case
            if custom_input is not None:
                current_output = run_code(
                    submission.language,
                    submission.code,
                    custom_input,
                    "Custom test - no expected output comparison"
                )
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'verdict': 'CUSTOM_TEST',
                        'input': custom_input,
                        'output': current_output,
                        'error': current_output if "error" in current_output.lower() or "exception" in current_output.lower() else '',
                    })
                
                return render(request, "submit/result.html", {
                    "submission": submission,
                    "problem": problem
                })

            # Get test cases based on action
            testcases = problem.testcases.filter(is_sample=True).order_by("order") if action == "run" \
                      else problem.testcases.all().order_by("order")

            combined_input = []
            combined_output = []
            combined_expected = []
            all_passed = True
            error_message = ""

            # Process each test case
            for testcase in testcases:
                current_input = testcase.input_data
                current_expected = testcase.expected_output
                current_output = run_code(
                    submission.language,
                    submission.code,
                    current_input,
                    current_expected,
                )

                try:
                    if "error" in current_output.lower() or "exception" in current_output.lower():
                        all_passed = False
                        error_message = current_output
                    elif current_output.strip() != current_expected.strip():
                        all_passed = False
                except Exception as e:
                    current_output = str(e)
                    all_passed = False
                    error_message = current_output

                combined_input.append(current_input)
                combined_output.append(current_output)
                combined_expected.append(current_expected)

            # Save submission results (only for non-custom tests)
            if custom_input is None:
                submission.input_data = "\n".join(combined_input)
                submission.output_data = "\n".join(combined_output)
                submission.expected_output = "\n".join(combined_expected)
                submission.verdict = 'ACCEPTED' if all_passed else 'REJECTED'
                
                if error_message:
                    submission.error_message = error_message
                
                # Get AI review only for submissions (not test runs)
                if action == "submit":
                    cache_key = f"ai_reviews_{request.user.id if request.user.is_authenticated else 'anon'}"
                    review_count = cache.get(cache_key, 0)
                    
                    if review_count < 5:  # Limit to 5 reviews per hour
                        submission.ai_review = get_ai_review(
                            submission.code,
                            submission.language,
                            problem.description
                        )
                        cache.set(cache_key, review_count + 1, 3600)  # 1 hour expiry
                    else:
                        submission.ai_review = "Hourly review limit reached (5 max)"
                
                submission.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'verdict': submission.verdict if custom_input is None else 'CUSTOM_TEST',
                    'input': submission.input_data if custom_input is None else custom_input,
                    'output': submission.output_data if custom_input is None else combined_output[0] if combined_output else current_output,
                    'error': error_message if error_message else '',
                    'ai_review': submission.ai_review if hasattr(submission, 'ai_review') else None
                })
            
            return render(request, "submit/result.html", {
                "submission": submission,
                "problem": problem
            })

    # GET request handling remains unchanged
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    form = CodeSubmissionForm()
    problems = Problem.objects.get(id=id)
    return render(request, 'submit/cp.html', {
        'problems': problems,
        'form': form,
    })

# run_code function remains exactly the same
def run_code(language, code, input_data, expected_output):
    project_path = Path(settings.BASE_DIR)
    directories = ["codes", "inputs", "outputs", "ex_outputs"]

    for directory in directories:
        dir_path = project_path / directory
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)

    codes_dir = project_path / "codes"
    inputs_dir = project_path / "inputs"
    outputs_dir = project_path / "outputs"
    ex_outputs_dir = project_path / "ex_outputs"

    unique = str(uuid.uuid4())

    code_file_name = f"{unique}.{language}"
    input_file_name = f"{unique}.txt"
    output_file_name = f"{unique}.txt"
    ex_outputs_file_name = f"{unique}.txt"

    code_file_path = codes_dir / code_file_name
    input_file_path = inputs_dir / input_file_name
    output_file_path = outputs_dir / output_file_name
    ex_outputs_file_path = ex_outputs_dir / ex_outputs_file_name

    with open(code_file_path, "w") as code_file:
        code_file.write(code)

    with open(input_file_path, "w") as input_file:
        input_file.write(input_data)

    with open(ex_outputs_file_path, "w") as ex_outputs_file:
        ex_outputs_file.write(expected_output)

    with open(output_file_path, "w") as output_file:
        pass  # create empty output file

    error_message = ""
    output_data = ""

    try:
        if language == "cpp":
            executable_path = codes_dir / unique
            compile_result = subprocess.run(
                ["g++", str(code_file_path), "-o", str(executable_path)],
                stderr=subprocess.PIPE,
                text=True
            )
            if compile_result.returncode != 0:
                error_message = compile_result.stderr
                raise subprocess.CalledProcessError(compile_result.returncode, compile_result.args)

            with open(input_file_path, "r") as input_file:
                with open(output_file_path, "w") as output_file:
                    run_result = subprocess.run(
                        [str(executable_path)],
                        stdin=input_file,
                        stdout=output_file,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    if run_result.returncode != 0:
                        error_message = run_result.stderr
        elif language == "c":  # <-- add this block for C
            executable_path = codes_dir / unique
            compile_result = subprocess.run(
                ["gcc", str(code_file_path), "-o", str(executable_path)],
                stderr=subprocess.PIPE,
                text=True
            )
            if compile_result.returncode != 0:
                error_message = compile_result.stderr
                raise subprocess.CalledProcessError(compile_result.returncode, compile_result.args)

            with open(input_file_path, "r") as input_file:
                with open(output_file_path, "w") as output_file:
                    run_result = subprocess.run(
                        [str(executable_path)],
                        stdin=input_file,
                        stdout=output_file,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    if run_result.returncode != 0:
                        error_message = run_result.stderr
        elif language == "py":
            with open(input_file_path, "r") as input_file:
                with open(output_file_path, "w") as output_file:
                    run_result = subprocess.run(
                        ["python3", str(code_file_path)],
                        stdin=input_file,
                        stdout=output_file,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    if run_result.returncode != 0:
                        error_message = run_result.stderr

        with open(output_file_path, "r") as output_file:
            output_data = output_file.read()

        if error_message:
            output_data = error_message

    except Exception as e:
        output_data = str(e)

    return output_data