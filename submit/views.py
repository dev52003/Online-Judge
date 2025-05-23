from django.shortcuts import render
from django.http import HttpResponse
from submit.forms import CodeSubmissionForm
from django.conf import settings
from problems.models import Problem
import uuid
import subprocess
from pathlib import Path



def submit(request,id):
    if request.method == "POST":
        form = CodeSubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save()
            print(submission.language)
            print(submission.code)
            problem_no = Problem.objects.get(id=id)
            submission.input_data = problem_no.testcase_inputs
            submission.expected_output = problem_no.ex_output
            submission.save()
            output = run_code(
                submission.language, submission.code, submission.input_data, submission.expected_output,
            )
            submission.output_data = output
        # submission.expected_output = ex_outputs
         #   submission.input_data = input
        
            
        try:
                if submission.output_data.strip() == submission.expected_output.strip():
                    submission.verdict = 'ACCEPTED'
                else:
                    submission.verdict = 'REJECTED'
        except Exception as e:
                submission.output_data = str(e)
                submission.verdict = 'Error'
        submission.save()
        return render(request, "submit/result.html", {"submission": submission})
    else:
        form = CodeSubmissionForm()
    problems = Problem.objects.get(id=id)
    context = {
        'problems' : problems,
        'form' : form,
    }
    return render(request, 'submit/cp.html', context)
    return render(request, "submit/cp.html", {"form": form})


def run_code(language, code, input_data,expected_output):
    project_path = Path(settings.BASE_DIR)
    directories = ["codes", "inputs", "outputs","ex_outputs"]

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
        pass  # This will create an empty file

    if language == "cpp":
        executable_path = codes_dir / unique
        compile_result = subprocess.run(
            ["g++", str(code_file_path), "-o", str(executable_path)]
        )
        if compile_result.returncode == 0:
            with open(input_file_path, "r") as input_file:
                with open(output_file_path, "w") as output_file:
                    subprocess.run(
                        [str(executable_path)],
                        stdin=input_file,
                        stdout=output_file,
                    )
    elif language == "py":
        # Code for executing Python script
        with open(input_file_path, "r") as input_file:
            with open(output_file_path, "w") as output_file:
                subprocess.run(
                    ["python3", str(code_file_path)],
                    stdin=input_file,
                    stdout=output_file,
                )

    # Read the output from the output file
    with open(output_file_path, "r") as output_file:
        output_data = output_file.read()

    with open(ex_outputs_file_path, "r") as ex_outputs_file:
        ex_outputs = ex_outputs_file.read()

    with open(input_file_path, "r") as input_file:
        input_data = input_file.read() 
        
    return output_data