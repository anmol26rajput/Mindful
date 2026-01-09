from django import forms
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
        fields = ['full_name', 'age', 'weight', 'location', 'primary_goal']
        widgets = {
            'primary_goal': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe your main goals...'}),
        }

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