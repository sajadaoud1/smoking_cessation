from rest_framework import serializers
from .models import *

class SmokingHabitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmokingHabits
        fields = '__all__'

class QuittingPlanSerializer(serializers.ModelSerializer):
    quit_date = serializers.ReadOnlyField()  # Read-only because it's a computed property
    cigs_per_day = serializers.IntegerField(source='smoking_habits.cigs_per_day', read_only=True)

    class Meta:
        model = QuittingPlan
        fields = [
            'user', 'plan_type', 'start_date', 'duration',
            'remaining_cigarettes', 'quit_date', 'cigs_per_day'
        ]

class DailySmokingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySmokingLog
        fields = '__all__'

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
    class Meta:
        model = Badge
        fields = ['id', 'name', 'description', 'icon']

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
        fields = ['id', 'username','first_name','last_name','email', 'phone_number', 'profile_picture', 'birth_date', 'gender', 'badges']
        read_only_fields = ['id', 'email', 'username']

