from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("phone_number", "profile_picture","gender","birth_date","achievements")}),
    )
    search_fields = ('username', 'email')

@admin.register(SmokingHabits)
class SmokingHabitAdmin(admin.ModelAdmin):
    model = SmokingHabits
    list_display = ('user', 'cigs_per_day', 'cigs_per_pack', 'pack_cost')
    search_fields = ('user__username',)

@admin.register(QuittingPlan)
class QuittingPlanAdmin(admin.ModelAdmin):
    model = QuittingPlan
    list_display = ('user', 'start_date', 'duration','quit_date')
    search_fields = ('user__username',)

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display=('user','days_without_smoking','money_saved','points')

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_earned','points')
    search_fields = ('user__username','name')

@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'Remind_at','is_sent')

@admin.register(ChatbotIteraction)
class ChatbotIteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_message', 'bot_response','timestamp')

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'icon')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'timestamp','is_read')
