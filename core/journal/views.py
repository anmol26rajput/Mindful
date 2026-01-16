from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import DailyEntry, UserProfile, OnboardingResponse, Habit, HabitCompletion, Feedback, Goal
from .forms import EntryForm, UserProfileForm, OnboardingForm, HabitForm, FeedbackForm, GoalForm
import json
from django.utils import timezone
import calendar
from datetime import datetime, timedelta
from django.urls import reverse
from django.http import HttpResponseRedirect

from django.core.mail import send_mail
from django.conf import settings
import random
from .models import EmailVerification
from .forms import CustomUserCreationForm, OTPForm

@api_view(['GET', 'POST'])
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until verified
            user.save()
            
            # Generate OTP
            code = f"{random.randint(100000, 999999)}"
            EmailVerification.objects.update_or_create(
                user=user,
                defaults={'code': code}
            )
            
            # Send Email
            send_mail(
                'Verify your email - Mindful Tracker',
                f'Your verification code is: {code}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            request.session['verification_user_id'] = user.id
            messages.info(request, f'Verification code sent to {user.email}')
            return redirect('verify_email')
    else:
        form = UserCreationForm()
    return render(request, 'journal/register.html', {'form': form})

from .forms import OTPForm

@api_view(['GET', 'POST'])
def verify_email(request):
    user_id = request.session.get('verification_user_id')
    if not user_id:
        return redirect('register')
        
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                verification = EmailVerification.objects.get(user_id=user_id)
                if verification.code == code and not verification.is_expired():
                    # Success
                    user = User.objects.get(id=user_id)
                    user.is_active = True
                    user.save()
                    verification.delete() # Cleanup
                    
                    # Login and redirect
                    from django.contrib.auth import login
                    login(request, user)
                    del request.session['verification_user_id']
                    
                    messages.success(request, 'Email verified! Welcome.')
                    return redirect('profile_setup')
                else:
                    messages.error(request, 'Invalid or expired code.')
            except EmailVerification.DoesNotExist:
                messages.error(request, 'Verification session invalid.')
                
    else:
        form = OTPForm()
        
    return render(request, 'journal/verify_email.html', {'form': form})

@login_required
@api_view(['GET', 'POST'])
def profile_setup(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('quiz_setup')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'journal/profile_form.html', {'form': form})

@login_required
@api_view(['GET', 'POST'])
def profile_overview(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    try:
        onboarding = OnboardingResponse.objects.filter(user=request.user).latest('completion_date')
    except OnboardingResponse.DoesNotExist:
        onboarding = None

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=profile)
        # Handle Onboarding edits if needed (e.g., goals)
        # For simplicity, we might just update the UserProfile fields here as requested
        
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile_overview')
    else:
        profile_form = UserProfileForm(instance=profile)

    return render(request, 'journal/profile_overview.html', {
        'profile_form': profile_form,
        'profile': profile,
        'onboarding': onboarding
    })

@login_required
@api_view(['GET', 'POST'])
def quiz_setup(request):
    if request.method == 'POST':
        form = OnboardingForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.user = request.user
            response.save()
            messages.success(request, "All set! Welcome to your dashboard.")
            return redirect('dashboard')
    else:
        form = OnboardingForm()
    return render(request, 'journal/quiz_form.html', {'form': form})

@login_required
# --- Helper Functions for Habits ---
def _handle_habit_post(request):
    if 'new_habit' in request.POST:
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            habit.save()
            messages.success(request, "Habit created!")
            return redirect('habits_list')
    elif 'delete_habit' in request.POST:
        habit_id = request.POST.get('habit_id')
        Habit.objects.filter(id=habit_id, user=request.user).delete()
        messages.success(request, "Habit deleted.")
        return redirect('habits_list')
    return None

@login_required
@api_view(['GET', 'POST'])
def habits_list(request):
    if request.method == 'POST':
        response = _handle_habit_post(request)
        if response:
            return response

    habits = Habit.objects.filter(user=request.user)
    form = HabitForm()
                
    return render(request, 'journal/habits.html', {
        'habits': habits,
        'form': form
    })

@login_required
# --- Helper Functions for Sleep Tracker ---
def _calculate_sleep_stats(entries):
    sleep_data = [entry.sleep_hours for entry in entries]
    
    # Avg Hours
    avg_hours = sum(sleep_data) / len(sleep_data) if sleep_data else 0
    avg_hours = round(avg_hours, 1)

    # Avg Quality (Heuristic)
    quality_sum = 0
    for hours in sleep_data:
        if hours >= 8: score = 5
        elif hours >= 7: score = 4
        elif hours >= 6: score = 3
        elif hours >= 5: score = 2
        else: score = 1
        quality_sum += score
    
    avg_quality = round(quality_sum / len(sleep_data), 1) if sleep_data else 0
    return sleep_data, avg_hours, avg_quality

@login_required
@api_view(['GET', 'POST'])
def sleep_tracker(request):
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            # Check if entry exists for date
            existing = DailyEntry.objects.filter(user=request.user, date=entry.date).first()
            if existing:
                existing.sleep_hours = entry.sleep_hours
                existing.save()
            else:
                entry.save()
            messages.success(request, "Sleep logged!")
            return redirect('sleep_tracker')

    # Data for graph
    entries = DailyEntry.objects.filter(user=request.user).order_by('date')
    dates = [entry.date.strftime("%b %d") for entry in entries]
    
    sleep_data, avg_hours, avg_quality = _calculate_sleep_stats(entries)

    form = EntryForm()
    return render(request, 'journal/sleep.html', {
        'dates': dates, 
        'sleep_data': sleep_data,
        'avg_hours': avg_hours,
        'avg_quality': avg_quality,
        'form': form
    })

@login_required
@api_view(['GET'])
def journal_list(request):
    entries = DailyEntry.objects.filter(user=request.user).order_by('-date')
    
    # Date Filtering
    date_filter = request.GET.get('date')
    if date_filter:
        entries = entries.filter(date=date_filter)
        
    return render(request, 'journal/journal_list.html', {
        'entries': entries,
        'date_filter': date_filter
    })


@login_required
# --- Helper Functions for Goals ---
def _handle_goal_post(request):
    if 'new_goal' in request.POST:
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.save()
            messages.success(request, "Goal set!")
            return redirect('goals_tracker')
    elif 'toggle_goal' in request.POST:
        goal_id = request.POST.get('goal_id')
        goal = get_object_or_404(Goal, id=goal_id, user=request.user)
        goal.is_completed = not goal.is_completed
        goal.save()
        return redirect('goals_tracker')
    elif 'delete_goal' in request.POST:
        goal_id = request.POST.get('goal_id')
        Goal.objects.filter(id=goal_id, user=request.user).delete()
        messages.success(request, "Goal deleted.")
        return redirect('goals_tracker')
    return None

@login_required
@api_view(['GET', 'POST'])
def goals_tracker(request):
    if request.method == 'POST':
        response = _handle_goal_post(request)
        if response:
            return response

    active_goals = Goal.objects.filter(user=request.user, is_completed=False)
    completed_goals = Goal.objects.filter(user=request.user, is_completed=True)
    form = GoalForm()
    
    return render(request, 'journal/goals.html', {
        'active_goals': active_goals,
        'completed_goals': completed_goals,
        'form': form
    })

# --- Helper Functions for Dashboard Refactoring ---

def _get_dashboard_date(request):
    """Determines and validates the view date."""
    today = timezone.now().date()
    view_date_str = request.GET.get('date') or request.POST.get('date')
    
    if view_date_str:
        try:
            view_date = datetime.strptime(view_date_str, '%Y-%m-%d').date()
        except ValueError:
            view_date = today
    else:
        view_date = today

    # Future Date Protection
    if view_date > today:
        messages.warning(request, "You cannot log entries for future dates.")
        view_date = today
        
    return view_date, today

def _handle_dashboard_post(request, view_date, day_entry):
    """Handles all POST actions for the dashboard."""
    redirect_url = f"{reverse('dashboard')}?date={view_date.strftime('%Y-%m-%d')}"
    
    if 'log_entry' in request.POST:
        form = EntryForm(request.POST, instance=day_entry)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.date = view_date
            entry.save()
            messages.success(request, "Entry saved successfully!")
            return HttpResponseRedirect(redirect_url)
            
    elif 'add_habit' in request.POST:
        habit_form = HabitForm(request.POST)
        if habit_form.is_valid():
            habit = habit_form.save(commit=False)
            habit.user = request.user
            habit.save()
            messages.success(request, "New habit added!")
            return HttpResponseRedirect(redirect_url)
            
    elif 'toggle_habit' in request.POST:
        habit_id = request.POST.get('toggle_habit')
        habit = get_object_or_404(Habit, id=habit_id, user=request.user)
        completion, created = HabitCompletion.objects.get_or_create(habit=habit, date=view_date)
        if not created:
            completion.delete()
        return HttpResponseRedirect(redirect_url)
        
    elif 'toggle_goal' in request.POST:
        goal_id = request.POST.get('goal_id')
        goal = get_object_or_404(Goal, id=goal_id, user=request.user)
        goal.is_completed = not goal.is_completed
        goal.save()
        return HttpResponseRedirect(redirect_url)
        
    return None

def _get_dashboard_context(request, view_date, today, day_entry):
    """Aggregates all data for the dashboard context."""
    user = request.user
    
    # 1. Forms
    form = EntryForm(instance=day_entry)
    habit_form = HabitForm()
    
    # 2. Daily Data
    active_habits = Habit.objects.filter(user=user, is_active=True)
    habit_data = []
    for habit in active_habits:
        is_completed = HabitCompletion.objects.filter(habit=habit, date=view_date).exists()
        habit_data.append({'habit': habit, 'completed': is_completed})
        
    daily_goals = Goal.objects.filter(user=user, created_at__date=view_date).order_by('id')
    active_goals_count = Goal.objects.filter(user=user, created_at__date=view_date, is_completed=False).count()
    completed_goals_count = Goal.objects.filter(user=user, created_at__date=view_date, is_completed=True).count()
    
    # 3. History & Charts (Last 7-30 days)
    entries_history = DailyEntry.objects.filter(user=user).order_by('date')
    dates = [e.date.strftime("%Y-%m-%d") for e in entries_history]
    sleep_data = [e.sleep_hours for e in entries_history]
    
    # 4. Consistency & Streak
    start_30_days_ago = today - timedelta(days=30)
    
    # Habit Consistency
    active_habits_count = active_habits.count()
    consistency_completions = HabitCompletion.objects.filter(
        habit__user=user, date__gte=start_30_days_ago, date__lte=today
    ).count()
    possible_completions_30d = active_habits_count * 30
    consistency_score = round((consistency_completions / possible_completions_30d) * 100, 1) if possible_completions_30d > 0 else 0
    
    # Goal Consistency
    total_goals_30d = Goal.objects.filter(
        user=user, created_at__date__gte=start_30_days_ago, created_at__date__lte=today
    ).count()
    completed_goals_30d = Goal.objects.filter(
        user=user, created_at__date__gte=start_30_days_ago, created_at__date__lte=today, is_completed=True
    ).count()
    goal_consistency_score = round((completed_goals_30d / total_goals_30d) * 100, 1) if total_goals_30d > 0 else 0

    # Streak
    completion_dates = sorted(list(set(HabitCompletion.objects.filter(habit__user=user, habit__is_active=True).values_list('date', flat=True))), reverse=True)
    current_streak = 0
    if completion_dates:
        latest_date = completion_dates[0]
        if latest_date == today or latest_date == today - timedelta(days=1):
            current_streak = 1
            check_date = latest_date
            for i in range(1, len(completion_dates)):
                if completion_dates[i] == check_date - timedelta(days=1):
                    current_streak += 1
                    check_date = completion_dates[i]
                else:
                    break

    # 5. Month Calendar Logic
    cal = calendar.Calendar()
    current_year = view_date.year
    current_month = view_date.month
    month_days = cal.monthdayscalendar(current_year, current_month)
    
    month_completions = HabitCompletion.objects.filter(
        habit__user=user, date__year=current_year, date__month=current_month
    ).values_list('date', flat=True)
    active_days = set(month_completions)
    active_day_numbers = {d.day for d in active_days}
    
    # Graph Data (Daily Completions for Month)
    from collections import Counter
    daily_counts = Counter(month_completions)
    habit_dates = []
    habit_completion_counts = []
    
    import calendar as cal_module
    _, num_days_in_month = cal_module.monthrange(current_year, current_month)
    for i in range(1, num_days_in_month + 1):
        d = view_date.replace(day=i)
        if d > today: break
        habit_dates.append(d.strftime("%Y-%m-%d"))
        habit_completion_counts.append(daily_counts[d])
        
    # Greeting
    current_hour = datetime.now().hour
    greeting = "Good morning" if current_hour < 12 else "Good afternoon" if current_hour < 18 else "Good evening"

    return {
        'form': form,
        'habit_form': habit_form,
        'entries': entries_history.reverse()[:7], 
        'dates': dates, 
        'sleep_data': sleep_data,
        'habit_data': habit_data,
        'daily_goals': daily_goals,
        'active_goals_count': active_goals_count,
        'completed_goals_count': Goal.objects.filter(user=user, is_completed=True).count(),
        'consistency_score': consistency_score,
        'goal_consistency_score': goal_consistency_score,
        'current_streak': current_streak,
        'month_days': month_days,
        'active_days': active_days,
        'active_day_numbers': active_day_numbers,
        'habit_dates': habit_dates,
        'habit_completion_counts': habit_completion_counts,
        'view_date': view_date,
        'today': today,
        'greeting': greeting,
        'current_month_name': today.strftime('%B %Y')
    }

@login_required
@api_view(['GET', 'POST'])
def dashboard(request):
    # Ensure profile exists
    if not hasattr(request.user, 'userprofile'):
        return redirect('profile_setup')

    view_date, today = _get_dashboard_date(request)
    day_entry = DailyEntry.objects.filter(user=request.user, date=view_date).first()

    if request.method == 'POST':
        response = _handle_dashboard_post(request, view_date, day_entry)
        if response:
            return response

    context = _get_dashboard_context(request, view_date, today, day_entry)
    return render(request, 'journal/dashboard.html', context)

@login_required
@api_view(['POST'])
def submit_feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.user = request.user
            feedback.save()
            messages.success(request, "Thank you for your feedback! ⭐")
        else:
            messages.error(request, "Something went wrong with your feedback.")
    
    # Redirect to the previous page where the user was
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))