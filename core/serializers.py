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

