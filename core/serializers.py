from rest_framework import serializers
from .models import *

class SmokingHabitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmokingHabits
        fields = '__all__'

class QuittingPlanSerializer(serializers.ModelSerializer):
    quit_date = serializers.ReadOnlyField()  # Read-only because it's a computed property

    class Meta:
        model = QuittingPlan
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

class CustomUserSerializer(serializers.ModelSerializer):
    badges = BadgeSerializer(many=True, read_only=True)  # Include badges in user profile

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone_number', 'profile_picture', 'badges']
