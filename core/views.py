from rest_framework import viewsets,permissions,status
from .serializers import *
from .models import *
from rest_framework.decorators import action
from rest_framework.response import Response
from .services import assign_quitting_plan,get_motivation_message

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

    def perform_create(self, serializer):
        user = self.request.user
        # check if the user has quitting plan
        quitting_plan, created = QuittingPlan.objects.get_or_create(user=user)
        duration = self.request.data.get("duration",quitting_plan.duration or 30)

        if not quitting_plan.smoking_habits:
            return Response({"error":"No smoking habits found."},status=status.HTTP_400_BAD_REQUEST)

        assign_quitting_plan(user,duration)

        serializer.save()
        return Response({"message": "Quitting plan updated successfully!", "plan_type": quitting_plan.plan_type}, status=status.HTTP_200_OK)

@action(detail=False, methods=["GET"],url_path="motivation")
def get_motivation_message(self,request):
    user = request.user
    message = get_motivation_message(user)
    return Response({"get_motivation_message": message},status=status.HTTP_200_OK)

class DailySmokingLogView(viewsets.ModelViewSet):
    serializer_class = DailySmokingLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DailySmokingLog.objects.filter(user=self.request.user).order_by('-date')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserProgressView(viewsets.ModelViewSet):
    serializer_class = UserProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user)

def perform_create(self, serializer):
    if UserProgress.objects.filter(user=self.request.user).exists():
        raise serializers.ValidationError("You already have a progress record.")
    serializer.save(user=self.request.user)

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

class CustomUserView (viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id) # Only return the logged-in user's profile

    @action(detail=True,methods=['post'])
    def add_badge(self, request, pk=None):
        user = self.get_object()
        badge_id = request.data.get('badge_id')

        try:
            badge = Badge.objects.get(id=badge_id)  # Check if the badge exists
        except Badge.DoesNotExist:
            return Response({'error': 'Badge not found'}, status=404)  # Return error if not found

        user.badges.add(badge)  # Assign the badge
        user.save()
        return Response({'message': f'Badge {badge.name} added to {user.username}!'})

class NotificationView(viewsets.ModelViewSet):
    serializer_class = NotificatinSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

