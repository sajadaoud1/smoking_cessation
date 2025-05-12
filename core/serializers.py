from rest_framework import serializers
from .models import *

class SmokingHabitsSerializer(serializers.ModelSerializer):
    triggers = serializers.ListField(
        child=serializers.ChoiceField(choices=SmokingHabits._meta.get_field('triggers').choices),
        allow_empty=True
    )
    class Meta:
        model = SmokingHabits
        fields = '__all__'
        read_only_fields = ['user']


class QuittingPlanSerializer(serializers.ModelSerializer):
    quit_date = serializers.ReadOnlyField()  # Read-only because it's a computed property
    cigs_per_day = serializers.IntegerField(source='smoking_habits.cigs_per_day', read_only=True)

    class Meta:
        model = QuittingPlan
        fields = [
            'user', 'plan_type', 'start_date', 'duration',
            'quit_date', 'cigs_per_day'
        ]
        read_only_fields = ['user', 'duration', 'plan_type', 'start_date']


class DailySmokingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySmokingLog
        fields = '__all__'
        read_only_fields = ['date','user']

class UserProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgress
        fields = '__all__'

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = '__all__'

class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = '__all__'

class ChatbotInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotIteraction
        fields = '__all__'

class BadgeSerializer(serializers.ModelSerializer):
    icon = serializers.ImageField(use_url = True)
    class Meta:
        model = Badge
        fields = ['name', 'description', 'icon']

class NotificatinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ["created_at"]

class CustomUserSerializer(serializers.ModelSerializer):
    badges = BadgeSerializer(many=True, read_only=True)  # Include badges in user profile
    achievements = AchievementSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username','first_name','last_name','email', 'phone_number', 'profile_picture', 'birth_date', 'gender', 'badges','achievements']
        read_only_fields = ['id', 'email', 'username']

