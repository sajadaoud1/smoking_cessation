from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    # no field for now
    pass

class SmokingHabits(models.Model):
    user = models.OneToOneField('CustomUser',on_delete=models.CASCADE)
    cigs_per_day = models.PositiveIntegerField(help_text="How many cigarettes do you smoke per day?")
    cigs_per_pack = models.PositiveIntegerField(help_text="How many cigarettes are in one pack?")
    pack_cost = models.DecimalField(max_digits=6,decimal_places=2,help_text="Cost of one pack.")

    def __str__(self):
        return f"{self.user.username}'s Smoking Habit"

class QuittingPlan(models.Model):
    user = models.OneToOneField('CustomUser',on_delete=models.CASCADE)
    start_date = models.DateField(default=timezone.now,help_text="The start date of the quitting plan.")
    duration = models.PositiveIntegerField(help_text="Duration of the quitting plan in days.")

    @property
    def quit_date(self):
        return self.start_date + timedelta(days=self.duration)
    
    def __str__(self):
        return f"{self.user.username}'s Quitting Plan"

class UserProgress(models.Model):
    user = models.OneToOneField('CustomUser',on_delete=models.CASCADE)
    days_without_smoking = models.PositiveIntegerField(default=0,help_text="Days the user has not smoked.")
    money_saved = models.DecimalField(max_digits=8,decimal_places=4,blank=True,help_text="Money saved by not buying cigarettes.")

    def __str__(self):
        return f"{self.user.username}'s Progress"
    
class Achievement(models.Model):
    user = models.ForeignKey('CustomUser',on_delete=models.CASCADE)
    name = models.CharField(max_length=255,help_text="Achievement title (e.g., '1 Week Smoke-Free')")
    description = models.TextField(help_text="Details about the achievement.")
    date_earned = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}-{self.name}"