from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from journal.models import UserProfile

class Command(BaseCommand):
    help = 'Checks for birthdays, sends emails, and updates age'

    def handle(self, *args, **options):
        today = timezone.now().date()
        # Filter profiles where birthday matches today
        profiles = UserProfile.objects.filter(
             date_of_birth__month=today.month,
             date_of_birth__day=today.day
        )
        
        count = 0
        for profile in profiles:
            # Update Age
            # For people born on Feb 29, consistent handling for non-leap years is tricky with exact match
            # But here we match exact month/day, so non-leap year Feb 28 won't match Feb 29.
            # Standard simple birthday logic.
            
            new_age = today.year - profile.date_of_birth.year
            
            if profile.age != new_age:
                profile.age = new_age
                profile.save()
                self.stdout.write(f"Updated age for {profile.user.username} to {new_age}")
            
            # Send Email
            if profile.user.email:
                try:
                    send_mail(
                        subject='Happy Birthday from Mindful Tracker! 🎉',
                        message=f'Hi {profile.user.username},\n\nWishing you a very Happy Birthday! May this year bring you closer to your goals and happiness.\n\nKeep tracking, stay mindful!\n\nBest,\nThe Mindful Tracker Team',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[profile.user.email],
                        fail_silently=False
                    )
                    count += 1
                    self.stdout.write(f"Sent birthday email to {profile.user.email}")
                except Exception as e:
                     self.stdout.write(self.style.ERROR(f"Failed to send email to {profile.user.email}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully processed {count} birthdays for {today}'))
