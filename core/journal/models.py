from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    weight = models.FloatField(help_text="Weight in kg", null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    primary_goal = models.TextField(help_text="What do you want to achieve?", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

class OnboardingResponse(models.Model):
    EXPERIENCE_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    why_here = models.TextField(help_text="Why are you using this site?", verbose_name="Reason for joining")
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='beginner')
    completion_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Onboarding for {self.user.username}"

class Habit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class HabitCompletion(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    completed = models.BooleanField(default=True)

    class Meta:
        unique_together = ('habit', 'date')

class DailyEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    gratitude = models.TextField(help_text="What are you grateful for today?")
    # habit_completed field is deprecated in favor of specific Habit tracking, 
    # but kept for migration safety or summary usage if needed.
    # We can perform a migration to remove it later or mark it editable=False.
    habit_completed = models.BooleanField(default=False, verbose_name="Habit System Legacy Field") 
    sleep_hours = models.FloatField(help_text="Hours slept last night")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date') # One entry per user per day
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date}"

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    deadline = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(help_text="Your feedback")
    rating = models.IntegerField(default=5, help_text="Rating from 1 to 5")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.username} - {self.rating} stars"