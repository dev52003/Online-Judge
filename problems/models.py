# from django.db import models

# # Create your models here.
# class Problem(models.Model):
#     title = models.CharField(max_length=255)
#     difficulty = models.CharField(max_length=50)
#     description = models.TextField()
#     input_format = models.TextField(null=True)
#     output_format = models.TextField(null=True)
#     example_input = models.TextField()
#     example_output = models.TextField()
#     testcase_inputs = models.TextField(null=True)
#     ex_output = models.TextField(null=True)


#     def __str__(self):
#         return self.title

from django.db import models

class Problem(models.Model):
    title = models.CharField(max_length=255)
    difficulty = models.CharField(max_length=50)
    description = models.TextField()
    input_format = models.TextField(null=True, blank=True)
    output_format = models.TextField(null=True, blank=True)
    example_input = models.TextField()
    example_output = models.TextField()

    def __str__(self):
        return self.title

class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='testcases')
    input_data = models.TextField()
    expected_output = models.TextField()
    is_sample = models.BooleanField(default=False)  # to distinguish sample from hidden test cases
    order = models.PositiveIntegerField(default=0)  # to order test cases if needed

    def __str__(self):
        return f"TestCase {self.order} for {self.problem.title}"
