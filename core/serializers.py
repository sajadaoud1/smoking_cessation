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
        models = Reminder
        fields = '__all__'

class ChatbotInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        models = ChatbotIteraction
        fields = '__all__'

class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        models = Badge
        fields = '__all__'

class NotificatinSerializer(serializers.ModelSerializer):
    class Meta:
        models = Notification
        fields = '__all__'
