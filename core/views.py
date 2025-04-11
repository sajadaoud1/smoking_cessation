<<<<<<< HEAD
from rest_framework import viewsets, permissions, status
=======
from rest_framework import viewsets,permissions,status
from django.shortcuts import get_object_or_404
from rest_framework.request import Request
from django.http import JsonResponse
>>>>>>> a6e566fabe5352b39a9b42f37f2db2ae05f921ca
from .serializers import *
from .models import *
from rest_framework.decorators import action
from rest_framework.response import Response
<<<<<<< HEAD
from .services import assign_quitting_plan, get_motivation_message
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated




=======
from core.utils.notification import send_push_notification
from .services import assign_quitting_plan,get_motivation_message
>>>>>>> a6e566fabe5352b39a9b42f37f2db2ae05f921ca

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
        return Achievement.objects.filter(users=self.request.user)

def complete_goal(request,user_id,goal_name):
    user = get_object_or_404(CustomUser,id=user_id)

    achievement = get_object_or_404(Achievement, name=goal_name)

    if not achievement:
        return JsonResponse({"error": "Achievement not found"}, status=404)
    
    user.achievements.add(achievement)

    Notification.objects.create(
        user = user,
        title = "Achievement Unloacked!",
        message = f"Congratulations! You unlocked '{achievement.name}' "
    )

    if user.fcm_token:
        send_push_notification(
            registration_token=user.fcm_token,
            title="Achievement Unlocked!",
            body=f"Congrats! You earned '{achievement.name}'"
        )
        
    return JsonResponse({        
        "message": f"Achievement '{goal_name}' awarded!",
        "achievements": list(user.achievements.values("name"))
    })


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

    @action(detail=False, methods=['post'])
    def save_fcm_token(self,request:Request):
        user: CustomUser = request.user
        token = request.data.get("fcm_token")

        if not token:
            return Response({"error":"Token is required"}, status=400)
        
        user.fcm_token = token
        user.save()
        return Response({"message":"FCM token saved successfully!"})

    @action(detail=True,methods=['post'])
    def add_badge(self, request:Request, pk=None):
        user: CustomUser = self.get_object()
        badge_id = request.data.get('badge_id')

        try:
            badge = Badge.objects.get(id=badge_id)  # Check if the badge exists
        except Badge.DoesNotExist:
            return Response({'error': 'Badge not found'}, status=404)  # Return error if not found

        user.badges.add(badge)  # Assign the badge
        user.save()
        return Response({'message': f'Badge {badge.name} added to {user.username}!'})


class RegisterUserView(APIView):
    def post(self,request):
        username=request.data.get('username')
        password=request.data.get('password')

        if user.objects.filter(username=username).exists():
           raise ValidationError("A user with this username already exists ")

        user = user.objects.create_user(username=username , password = password)
        token = Token.objects.create(user=user)

        return Response({
            'message': 'User Registered successfully ! ',
            'token': token.key 
        } , status= status.HTTP_201_CREATED)

 class LoginView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

 class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # Only logged-in users can log out

    def post(self, request):
        try:
            # Delete the user's token
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response({'message': 'Logged out successfully!'}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'error': 'No active session found.'}, status=status.HTTP_400_BAD_REQUEST)



class NotificationView(viewsets.ModelViewSet):
    serializer_class = NotificatinSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        notifications.update(is_read=True)
        return Response({"message": "All notifications marked as read!"})
    
    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read= True
        notification.sava()
        return Response({"message": f"Notification '{notification.title}' marked as read!"})