from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
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