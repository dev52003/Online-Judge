from django.db import models

# Create your models here.
class Problem(models.Model):
    title = models.CharField(max_length=255)
    difficulty = models.CharField(max_length=50)
    description = models.TextField()
    input_format = models.TextField(null=True)
    output_format = models.TextField(null=True)
    example_input = models.TextField()
    example_output = models.TextField()
    testcase_inputs = models.TextField(null=True)
    ex_output = models.TextField(null=True)


    def __str__(self):
        return self.title