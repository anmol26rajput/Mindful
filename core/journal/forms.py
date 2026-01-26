from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import DailyEntry, UserProfile, OnboardingResponse, Habit, Feedback, Goal

class EntryForm(forms.ModelForm):
    class Meta:
        model = DailyEntry
        fields = ['date', 'gratitude', 'sleep_hours'] # Removed habit_completed
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'gratitude': forms.Textarea(attrs={'rows': 3, 'placeholder': 'I am grateful for...'}),
            'sleep_hours': forms.NumberInput(attrs={'step': 0.5, 'min': 0, 'max': 24}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'date_of_birth', 'age', 'weight', 'location', 'primary_goal']
        widgets = {
            'primary_goal': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe your main goals...'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Disable fields that shouldn't be edited if they are already set
        if self.instance and self.instance.pk:
            protected_fields = ['full_name', 'date_of_birth', 'age', 'weight', 'location']
            for field in protected_fields:
                if getattr(self.instance, field):
                    self.fields[field].widget.attrs['disabled'] = 'disabled'
                    self.fields[field].widget.attrs['readonly'] = True
                    self.fields[field].required = False

class OnboardingForm(forms.ModelForm):
    class Meta:
        model = OnboardingResponse
        fields = ['why_here', 'experience_level']
        widgets = {
            'why_here': forms.Textarea(attrs={'rows': 3, 'placeholder': 'I want to track my habits because...'}),
            'experience_level': forms.RadioSelect, 
        }

class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., Drink 2L Water'}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['message', 'rating']

class GoalForm(forms.ModelForm):
    deadline = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    class Meta:
        model = Goal
        fields = ['title', 'deadline']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us what you think...'}),
            'rating': forms.HiddenInput(),
        }

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='')
    date_of_birth = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = User
        fields = ['username', 'email'] # Explicit order (DOB handled manually in view)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove help text from all fields
        for field_name in self.fields:
            self.fields[field_name].help_text = None
        
        # Ensure Email is second (though Meta.fields usually handles this, we can enforce)
        # Custom styling
        self.fields['email'].widget.attrs.update({
            'placeholder': 'Email Address',
            'class': 'form-control ps-3 py-2 border-0',
            'style': 'background-color: rgba(255, 255, 255, 0.05); color: var(--text-main);'
        })
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Username',
            'class': 'form-control ps-3 py-2 border-0',
            'style': 'background-color: rgba(255, 255, 255, 0.05); color: var(--text-main);'
        })
        self.fields['date_of_birth'].widget.attrs.update({
            'class': 'form-control ps-3 py-2 border-0',
            'style': 'background-color: rgba(255, 255, 255, 0.05); color: var(--text-main);'
        })
        # Add style to password fields as well (inherited from UserCreationForm)
        # Add style and placeholder to password fields as well (inherited from UserCreationForm)
        for field_name in self.fields:
             if field_name not in ['email', 'username', 'date_of_birth']:
                label = self.fields[field_name].label
                self.fields[field_name].widget.attrs.update({
                    'placeholder': label,
                    'class': 'form-control ps-3 py-2 border-0',
                    'style': 'background-color: rgba(255, 255, 255, 0.05); color: var(--text-main);'
                })

class OTPForm(forms.Form):
    code = forms.CharField(max_length=6, min_length=6, widget=forms.TextInput(attrs={
        'placeholder': 'Enter 6-digit code',
        'class': 'form-control text-center text-spacing-4 fs-4',
        'autocomplete': 'off',
        'pattern': '[0-9]*',
        'inputmode': 'numeric'
    }))

class ChangeEmailForm(forms.Form):
    new_email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter new email address',
            'class': 'form-control ps-3 py-2 border-0',
            'style': 'background-color: rgba(255, 255, 255, 0.05); color: var(--text-main);'
        })
    )