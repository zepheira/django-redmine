from django import forms

class SupportIssueForm(forms.Form):
    subject = forms.CharField(max_length=100)
    file_link = forms.CharField(max_length=200)
