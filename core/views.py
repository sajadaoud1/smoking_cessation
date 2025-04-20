from rest_framework import viewsets, permissions, status
from django.shortcuts import get_object_or_404
from rest_framework.request import Request
from django.http import JsonResponse
from .serializers import *
from .models import *
from datetime import datetime
from rest_framework.decorators import action, api_view,permission_classes
from rest_framework.response import Response
from .services import assign_quitting_plan, get_motivation_message
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated,AllowAny
from core.utils.notification import send_push_notification
from .services import *
from rest_framework.permissions import IsAuthenticated
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from core.utils.notification import send_push_notification
from .services import assign_quitting_plan,get_motivation_message

FCM_TOKEN_KEY = "fcm_token"

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
        duration = 28

        if not quitting_plan.smoking_habits:
            return Response({"error":"No smoking habits found."},status=status.HTTP_400_BAD_REQUEST)

        result = assign_quitting_plan(user)

        serializer.save()

        return Response({
            "message": "Quitting plan created successfully!",
            "plan": result
        }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_motivation_message_view(request: Request):
    message = get_motivation_message(request.user)
    return Response({"motivation_message": message}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_reduction_schedule(request:Request):
    user:CustomUser = request.user
    quitting_plan:QuittingPlan = QuittingPlan.objects.filter(user=user).first()

    if not quitting_plan or not quitting_plan.smoking_habits:
        return Response({"error": "No plan or smoking habits found."}, status=404)

    cigs_per_day = quitting_plan.smoking_habits.cigs_per_day
    plan_type = quitting_plan.plan_type

    if plan_type == "Gradual Reduction":
        schedule = generate_weekly_reduction_schedule(cigs_per_day,weeks=4)
    else:
        schedule = [{"week": i + 1, "target_per_day": 0} for i in range(4)]

    return Response({
        "plan_type": quitting_plan.plan_type,
        "start_date": quitting_plan.start_date,
        "quit_date": quitting_plan.quit_date,
        "reduction_schedule": schedule
    })

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
    
@api_view(["GET"]) 
@permission_classes([IsAuthenticated])
def complete_goal(request,user_id,goal_name):
    user = get_object_or_404(CustomUser,id=user_id)

    achievement = get_object_or_404(Achievement, name=goal_name)
    user.achievements.add(achievement)

    Notification.objects.create(
        user = user,
        title = "Achievement Unlocked!",
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
        token = request.data.get(FCM_TOKEN_KEY)

        if not token:
            return Response({"error":"Token is required"}, status=400)
        
        user.fcm_token = token
        user.save()
        return Response({"message":"FCM token saved successfully!"})

    @action(detail=True,methods=['post'])
    def add_badge(self, request:Request, pk=None):
        user: CustomUser = self.get_queryset().filter(pk=pk).first()
        badge_id = request.data.get('badge_id')

        try:
            badge = Badge.objects.get(id=badge_id)  # Check if the badge exists
        except Badge.DoesNotExist:
            return Response({'error': 'Badge not found'}, status=404)  # Return error if not found

        user.badges.add(badge)  # Assign the badge
        user.save()
        return Response({'message': f'Badge {badge.name} added to {user.username}!'})

    @action(detail=False,methods=['get'])
    def view_profile(self,request:Request):
        user: CustomUser = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put','patch'])
    def update_profile(self,request:Request):
        user: CustomUser = request.user
        serializer = self.get_serializer(user, data=request.data, files= request.FILES, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Profile updated successfully","data":serializer.data})
        return Response(serializer.errors,status=400)

    @action(detail=False, methods=['get'])
    def me(self, request:Request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def change_password(self,request:Request):
        user: CustomUser = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response({"error":"Incorrect old password."},status=400)
        
        user.set_password(new_password)
        user.save()
        return Response({"message":"Password updated successfuly!"})

class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request:Request):
        username = request.data.get('username')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        password = request.data.get('password')
        phone = request.data.get('phone')
        gender = request.data.get('gender')
        birth_date = request.data.get('birth_date')

        # Validate email and phone uniqueness
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        if CustomUser.objects.filter(phone_number=phone).exists():
            raise ValidationError("A user with this phone number already exists.")
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("A user with this username already exists.")

        # Validate password and other fields
        validate_password(password)
        try:
            birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError("Invalid birth date format. Use YYYY-MM-DD.")

        # Create user
        user = CustomUser.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name, 
            email=email,
            password=password,
            phone_number=phone,
            gender=gender,
            birth_date=birth_date
        )
        token = Token.objects.create(user=user)

        return Response({
            'message': 'User registered successfully!',
            'token': token.key
        }, status=status.HTTP_201_CREATED)

class LoginView(ObtainAuthToken):
    def post(self, request:Request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request:Request):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response({'message': 'Logged out successfully!'}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({'error': 'No active session found.'}, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    def post(self, request:Request):
        email = request.data.get('email')
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"error": "No user found with this email."}, status=status.HTTP_404_NOT_FOUND)

        reset_token = get_random_string(length=32)
        user.reset_token = reset_token
        user.save()

        reset_link = f"http://yourfrontend.com/reset-password/{reset_token}"
        send_mail(
            'Password Reset Request',
            f'Click the link below to reset your password:\n\n{reset_link}',
            'yourapp@example.com',
            [email]
        )

        return Response({'message': 'Password reset link sent successfully!'}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    def post(self, request, reset_token):
        new_password = request.data.get('new_password')

        try:
            user = CustomUser.objects.get(reset_token=reset_token)
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid or expired reset token."}, status=status.HTTP_404_NOT_FOUND)

        validate_password(new_password)

        user.set_password(new_password)
        user.reset_token = None
        user.save()

        return Response({'message':'Password reset sucessfully!'}, status=status.HTTP_200_OK)

class NotificationView(viewsets.ModelViewSet):
    serializer_class = NotificatinSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request:Request):
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        notifications.update(is_read=True)
        return Response({"message": "All notifications marked as read!"})
    
    @action(detail=True, methods=["post"])
    def mark_as_read(self, request, pk=None):
        notification = self.get_queryset().filter(pk=pk).first()
        notification.is_read= True
        notification.save()
        return Response({"message": f"Notification '{notification.title}' marked as read!"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request:Request):
    user:CustomUser = request.user

    profile_data ={
        "username":user.username,
        "email":user.email,
        "phone_number":user.phone_number,
        "gender":user.gender,
        "birth_date":user.birth_date,
        "profile_picture":user.profile_picture.url if user.profile_picture else "/media/profile_pics/default.png",
    }

    smoking_habits = SmokingHabits.objects.filter(user=user).first()
    smoking_data = SmokingHabitsSerializer(smoking_habits).data if smoking_habits else {}

    progress = UserProgress.objects.filter(user=user).first()
    progress_data = UserProgressSerializer(progress).data if progress else {}

    quitting_plan = QuittingPlan.objects.filter(user=user).first()
    quitting_data = QuittingPlanSerializer(quitting_plan).data if quitting_plan else {}

    achievements = user.achievements.values("name","description","date_earned")
    badges = user.badges.values("name", "description")

    notifications = Notification.objects.filter(user=user).order_by("-timestamp")[:5]
    notifications_data = NotificatinSerializer(notifications,many=True).data

    if progress and smoking_habits:
        cigs_per_day = smoking_habits.cigs_per_day
        cigs_per_pack = smoking_habits.cigs_per_pack
        pack_cost = float(smoking_habits.pack_cost)

        daily_cost = (cigs_per_day/cigs_per_pack)*pack_cost
        total_saved = round(daily_cost*progress.days_without_smoking,2)

    else:
        total_saved = 0.00

    return Response({
        "profile": profile_data,
        "smoking_habits":smoking_data,
        "progress":progress_data,
        "quitting_plan":quitting_data,
        "achievement":list(achievements),
        "badges":list(badges),
        "recent_notifications":notifications_data,
        "money_saved":f"{total_saved} JD"
    })