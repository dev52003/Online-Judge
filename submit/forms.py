from django import forms
from submit.models import CodeSubmission

LANGUAGE_CHOICES = [
    ("cpp", "C++"),
    ("py", "Python"),
    ("c", "C"),
    
]


class CodeSubmissionForm(forms.ModelForm):
    language = forms.ChoiceField(choices=LANGUAGE_CHOICES)

    class Meta:
        model = CodeSubmission
        fields = ["language", "code"]
        widgets = {
            'code': forms.Textarea(attrs={
                'cols': 80, 
                'rows': 20,
                'class': 'textarea-code'
            }),
        }