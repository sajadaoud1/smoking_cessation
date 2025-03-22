from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15,unique=True,null=True,blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/',null=True,blank=True,default='profile_pics/default.png')

    def __str__(self):
        return self.username

class SmokingHabits(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    cigs_per_day = models.PositiveIntegerField(help_text="How many cigarettes do you smoke per day?")
    cigs_per_pack = models.PositiveIntegerField(help_text="How many cigarettes are in one pack?")
    pack_cost = models.DecimalField(max_digits=6,decimal_places=2,help_text="Cost of one pack.")

    def __str__(self):
        return f"{self.user.username}'s Smoking Habit"

class QuittingPlan(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now,help_text="The start date of the quitting plan.")
    duration = models.PositiveIntegerField(help_text="Duration of the quitting plan in days.")

    @property
    def quit_date(self):
        return self.start_date + timedelta(days=self.duration)
    
    def __str__(self):
        return f"{self.user.username}'s Quitting Plan"

class UserProgress(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    days_without_smoking = models.PositiveIntegerField(default=0,help_text="Days the user has not smoked.")
    money_saved = models.DecimalField(max_digits=8,decimal_places=4,blank=True,help_text="Money saved by not buying cigarettes.")
    points = models.PositiveIntegerField(default=0, help_text="Total points earned for progress.")
    
    def __str__(self):
        return f"{self.user.username}'s Progress"

class Achievement(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,help_text="Achievement title (e.g., '1 Week Smoke-Free')")
    name = models.CharField(max_length=255,help_text="Achievement title (e.g., '1 Week Smoke-Free')")
    description = models.TextField(help_text="Details about the achievement.")
    date_earned = models.DateField(default=timezone.now)
    points = models.PositiveIntegerField(default=0, help_text="Points for this achievement.")  # NEW FIELD

    def __str__(self):
        return f"{self.user.username}-{self.name}"

class Reminder(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    message = models.TextField()
    Remind_at = models.DateTimeField(help_text="Time when the reminder should be triggered.")
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Reminder for {self.user.username} at {self.Remind_at}"

class ChatbotIteraction(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    user_message = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, help_text="Time when the message was sent or received.")

    def __str__(self):
        return f"Chatbot interaction with {self.user.username} - {'User' if self.is_user else 'Bot'}: {self.message[:20]}"

class Badge(models.Model):
    name = models.CharField(max_length=255,help_text="Badge name.")
    description = models.TimeField(help_text="What this badge for.")
    icon = models.ImageField(upload_to='badges/',blank=True,null=True,help_text="Badge image.")

    def __str__(self):
        return self.name
    
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField(help_text="Notification content.")
    timestamp = models.DateTimeField(default=timezone.now, help_text="When the notification was created.")
    is_read = models.BooleanField(default=False, help_text="Has the user seen this notification?")

    def __str__(self):
        return f"{self.user.username} - {self.message[:20]}"