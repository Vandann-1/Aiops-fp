from django import forms
from .models import Incident

class IncidentCreateForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['title', 'category', 'priority', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Apache Server Not Responding'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe the issue in detail. What services are affected? Are there error messages? When did it start?'
            }),
        }
        help_texts = {
            'description': 'Be as specific as possible. The AI engine will use this description to locate recovery runbooks.'
        }


class IncidentAdminUpdateForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['priority', 'status']
        widgets = {
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
