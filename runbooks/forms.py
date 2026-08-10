from django import forms
from .models import Runbook

class RunbookForm(forms.ModelForm):
    class Meta:
        model = Runbook
        fields = [
            'title',
            'category',
            'description',
            'symptoms',
            'steps',
            'risk_level',
            'automation_action',
            'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Restart Apache Web Server'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the specific problem this runbook solves. Clear text is vital for semantic AI search.'
            }),
            'symptoms': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter symptoms (one per line, e.g.):\nWebsite unavailable\nConnection refused\nApache service inactive'
            }),
            'steps': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Enter the step-by-step procedures (e.g.):\n1. Check service status.\n2. Restart service.'
            }),
            'risk_level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'automation_action': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., restart_apache (optional)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        help_texts = {
            'description': 'Explain the exact technical scope of this troubleshooting procedure.',
            'symptoms': 'List keywords or common messages that indicate this runbook should be used.',
            'automation_action': 'Associated allowlisted script identifier (safe automation phase).'
        }
