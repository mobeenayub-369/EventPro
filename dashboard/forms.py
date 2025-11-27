from django import forms
from .models import UserDashboard, DashboardWidget

class DashboardPreferencesForm(forms.ModelForm):
    class Meta:
        model = UserDashboard
        fields = ['preferred_view']
        widgets = {
            'preferred_view': forms.Select(attrs={'class': 'form-control'}),
        }

class WidgetSettingsForm(forms.ModelForm):
    class Meta:
        model = DashboardWidget
        fields = ['title', 'position', 'is_visible']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_visible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )