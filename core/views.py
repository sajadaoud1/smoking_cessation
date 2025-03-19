from rest_framework import viewsets,permissions
from .serializers import *
from .models import *

class SmokingHabitsView(viewsets.ModelViewSet):
    queryset = SmokingHabits.objects.all()
    serializer_class = SmokingHabitsSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can access


class QuittingPlanView(viewsets.ModelViewSet):
    queryset = QuittingPlan.objects.all()
    serializer_class = QuittingPlanSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can access

    def perform_create(self,serializer):
        # Ensure the user can only create one quitting plan
        if QuittingPlan.objects.filter(user=self.request.user).exists():
            raise serializers.ValidationError("You already have a quitting plan.")
        serializer.save(user=self.request.user)  # Assign the authenticated user
