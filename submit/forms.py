# from django import forms
# from submit.models import CodeSubmission

# LANGUAGE_CHOICES = [
#     ("cpp", "C++"),
#     ("py", "Python"),
#     ("c", "C"),
    
# ]

# class CodeSubmissionForm(forms.ModelForm):
#     language = forms.ChoiceField(
#         choices=LANGUAGE_CHOICES,
#         widget=forms.Select(attrs={
#             'class': 'form-control'
#         })
#     )

#     class Meta:
#         model = CodeSubmission
#         fields = ["language", "code"]
#         widgets = {
#             'code': forms.Textarea(attrs={
#                 'style': 'display: none;'  # Hidden since CodeMirror will replace it
#             }),
#         }

# # class CodeSubmissionForm(forms.ModelForm):
# #     language = forms.ChoiceField(choices=LANGUAGE_CHOICES)

# #     class Meta:
# #         model = CodeSubmission
# #         fields = ["language", "code"]
# #         widgets = {
# #             'code': forms.Textarea(attrs={
# #                 'cols': 80, 
# #                 'rows': 20,
# #                 'class': 'textarea-code'
# #             }),
# #         }
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
                'id': 'code-editor',  # Added ID for JavaScript targeting
                'cols': 80, 
                'rows': 20,
                'class': 'textarea-code'
            }),
        }