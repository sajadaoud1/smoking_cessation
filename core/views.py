from rest_framework import viewsets,permissions
from .serializers import *
from .models import *

class SmokingHabitsView(viewsets.ModelViewSet):
    serializer_class = SmokingHabitsSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can access

    def get_queryset(self):
        return SmokingHabits.objects.filter(user=self.request.user)

class QuittingPlanView(viewsets.ModelViewSet):
    serializer_class = QuittingPlanSerializer
    permission_classes = [permissions.IsAuthenticated]  

    def get_queryset(self):
        return QuittingPlan.objects.filter(user=self.request.user)
    
    def perform_create(self,serializer):
        # Ensure the user can only create one quitting plan
        if QuittingPlan.objects.filter(user=self.request.user).exists():
            raise serializers.ValidationError("You already have a quitting plan.")
        serializer.save(user=self.request.user)  # Assign the authenticated user

class UserProgressView(viewsets.ModelViewSet):
    serializer_class = UserProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user)

class AchievementView(viewsets.ModelViewSet):
    serializer_class = AchievementSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        return Achievement.objects.filter(user=self.request.user)

class ReminderView(viewsets.ModelViewSet):
    serializer_class = ReminderSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user)

class ChatbotInteractionView(viewsets.ModelViewSet):
    serializer_class = ChatbotInteractionSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatbotIteraction.objects.filter(user=self.request.user)

class BadgeView(viewsets.ModelViewSet):
    serializer_class = BadgeSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        return Badge.objects.filter(user=self.request.user)

class NotificationView(viewsets.ModelViewSet):
    serializer_class = NotificatinSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

