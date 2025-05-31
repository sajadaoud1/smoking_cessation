from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from django.utils.html import format_html
# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("phone_number", "profile_picture","gender","birth_date","achievements","years_of_smoking")}),
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
    list_display=('user','days_without_smoking')

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_earned')
    search_fields = ('user__username','name')

@admin.register(ChatbotIteraction)
class ChatbotIteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_message', 'bot_response','timestamp')

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'badge_image_preview')

    def badge_image_preview(self, obj):
        if obj.icon:
            return format_html('<img src="{}" width="80" height="80" style="object-fit: contain;" />', obj.icon.url)
        return "No Image"

    badge_image_preview.short_description = 'Preview'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'timestamp','is_read')

@admin.register(DailySmokingLog)
class DailySmokingLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'cigarettes_smoked')
