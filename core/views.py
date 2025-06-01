from rest_framework import viewsets, permissions, status
from django.shortcuts import get_object_or_404
from rest_framework.request import Request
from django.http import JsonResponse
from .serializers import *
from core.models import *
from datetime import datetime,time
from rest_framework.decorators import action, api_view,permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from django.contrib.auth.password_validation import validate_password
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated,AllowAny
from core.utils.notification import send_push_notification
from .services import *
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from core.utils.notification import send_push_notification
from django.utils import timezone
from core.utils.xp_utils import award_dynamic_xp
FCM_TOKEN_KEY = "fcm_token"

class SmokingHabitsView(viewsets.ModelViewSet):
    serializer_class = SmokingHabitsSerializer
    permission_classes = [permissions.IsAuthenticated]  # Only authenticated users can access

    def get_queryset(self):
        return SmokingHabits.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class QuittingPlanView(viewsets.ModelViewSet):
    serializer_class = QuittingPlanSerializer
    permission_classes = [permissions.IsAuthenticated]  

    def get_queryset(self):
        return QuittingPlan.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        # check if the user has quitting plan
        if QuittingPlan.objects.filter(user=user).exists():
            return Response({"error": "Quitting plan already exists."}, status=status.HTTP_400_BAD_REQUEST)
        
        smoking_habits = SmokingHabits.objects.filter(user=user).first()

        if not smoking_habits:
            return Response({"error":"No smoking habits found."},status=status.HTTP_400_BAD_REQUEST)

        quitting_plan = QuittingPlan.objects.create(
            user=user,
            smoking_habits=smoking_habits,
            duration=28,  
        )
        result = assign_quitting_plan(user)

        UserProgress.objects.get_or_create(user=user)

        return Response({
            "message": "Quitting plan created successfully!",
            "plan": result
        }, status=status.HTTP_200_OK)

    @action(detail=False,methods=['get'],url_path='schedule')
    def schedule(self, request:Request):
        user:CustomUser = request.user

        quitting_plan:QuittingPlan = QuittingPlan.objects.filter(user=user).first()

        if not quitting_plan or not quitting_plan.smoking_habits:
            return Response({"error": "No plan or smoking habits found."}, status=404)

        smoking_habits :SmokingHabits = quitting_plan.smoking_habits
        cigs_per_day = smoking_habits.cigs_per_day
        plan_type = quitting_plan.plan_type

        if plan_type == "Gradual Reduction":
            schedule = generate_weekly_reduction_schedule(cigs_per_day)
        else:
            total_days = quitting_plan.duration
            num_weeks = total_days // 7
            schedule = [{"week": i + 1, "target_per_day": 0} for i in range(num_weeks)]

        return Response({
            "plan_type": quitting_plan.plan_type,
            "start_date": quitting_plan.start_date,
            "quit_date": quitting_plan.quit_date,
            "reduction_schedule": schedule
        })

class DailySmokingLogView(viewsets.ModelViewSet):
    queryset = DailySmokingLog.objects.all()
    serializer_class = DailySmokingLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if not is_within_checkin_time():
            raise ValidationError("You can only check in between 9:00 PM and 11:59 PM.")

        today = timezone.now().date()
        user = self.request.user

        if DailySmokingLog.objects.filter(user=user,date=today).exists():
            raise ValidationError("You have already checked in for today.")

        smoked_today = serializer.validated_data.get('cigarettes_smoked',0)
        self.saved_log = serializer.save(user=user,date=today)
        update_smoking_progress(user,smoked_today)
        update_user_progress(user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "data": DailySmokingLogSerializer(self.saved_log).data,
            "message": self.get_motivation_message(self.saved_log.cigarettes_smoked)
        }, status=status.HTTP_201_CREATED)
    
    def get_motivation_message(self,cigs_smoked):
        user = self.request.user
        target = get_target_for_today(user)
        if cigs_smoked == 0:
            message = "Amazing! You didn't smoke at all day, keep it up."
        elif cigs_smoked <= target:
            message = f"Great job! You smoked ({cigs_smoked}) which is less than your target ({target}), keep it up."
        else:
            message = f"You smoked ({cigs_smoked}) which is more than your target ({target}), don't give up and try again tomorrow."
        
        return message
    
    @action(detail=False, methods=["post"],url_path="checkin_no")
    def checkin_no(self,request):
        if not is_within_checkin_time():
            raise ValidationError("You can only check in between 9:00 PM and 11:59 PM.")

        user = request.user
        today = timezone.now().date()

        if DailySmokingLog.objects.filter(user=user,date=today).exists():
            raise ValidationError("You have already checked in for today.")


        log = DailySmokingLog.objects.create(
            user =user,
            date = today,
            cigarettes_smoked=0
        )

        update_smoking_progress(user,0)

        return Response({
            "data": DailySmokingLogSerializer(log).data,
            "message":"Amazing! You didn't smoke at all day, keep it up."
        },status= status.HTTP_201_CREATED)

def is_within_checkin_time():
    now = timezone.localtime().time()
    start_time = time(21,0)
    end_time = time(23,59)
    return start_time <= now <= end_time

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
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def achievements_and_badges(request:Request):
    user:CustomUser = request.user
    achievements = AchievementSerializer(user.achievements.all(),many=True).data
    badges = BadgeSerializer(user.badges.all(),many=True).data
    return Response({
        "achievements": achievements,
        "badges":badges
        })

@api_view(["GET"]) 
@permission_classes([IsAuthenticated])
def complete_goal(request,user_id,goal_name):
    user = get_object_or_404(CustomUser,id=user_id)

    achievement = get_object_or_404(Achievement, name=goal_name)
    if not user.achievements.filter(id=achievement.id).exists():
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
    
    else:
        return JsonResponse({
            "message":f"Achievement'{goal_name}' already unlocked",
            "achievement":list(user.achievements.values("name"))
        })

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

        allowed_fields = ['first_name','last_name','gender','birth_date']
        updated_data = {field: request.data.get(field) for field in allowed_fields if request.data.get(field)is not None}

        serializer = self.get_serializer(user, data=request.data ,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Profile updated successfully","data":serializer.data})
        return Response(serializer.errors,status=400)

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
        years_of_smoking = request.data.get('years_of_smoking')

        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        if CustomUser.objects.filter(phone_number=phone).exists():
            raise ValidationError("A user with this phone number already exists.")
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("A user with this username already exists.")

        validate_password(password)
        try:
            birth_date = datetime.strptime(birth_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError("Invalid birth date format. Use YYYY-MM-DD.")

        user = CustomUser.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name, 
            email=email,
            password=password,
            phone_number=phone,
            gender=gender,
            birth_date=birth_date,
            years_of_smoking=years_of_smoking
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
    permission_classes = [AllowAny]
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
    permission_classes = [AllowAny]
    def post(self, request:Request, reset_token):
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
        return Notification.objects.filter(user=self.request.user).order_by("-timestamp")

    @action(detail=False, methods=["patch"])
    def mark_all_read(self, request:Request):
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        notifications.update(is_read=True)
        return Response({"message": "All notifications marked as read!"})
    
    @action(detail=True, methods=["patch"])
    def mark_as_read(self, request, pk=None):
        notification = self.get_queryset().filter(pk=pk).first()

        if not notification:
            return Response(
                {"error":"Notification not found."},status=status.HTTP_404_NOT_FOUND
            )

        notification.is_read= True
        notification.save()
        return Response({"message": f"Notification '{notification.title}' marked as read!"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request: Request):
    user: CustomUser = request.user
    update_user_progress(user)

    target_currency = request.query_params.get("currency")

    progress, _ = UserProgress.objects.get_or_create(user=user)
    progress_data = UserProgressSerializer(progress).data if progress else {}

    notifications = Notification.objects.filter(user=user).order_by("-timestamp")[:5]
    notifications_data = NotificatinSerializer(notifications, many=True).data

    cigarettes_avoided = calculate_cigarettes_avoided(user)
    streak = progress.streak_days if progress else 0

    total_saved = calculate_money_saved(user, target_currency=target_currency)

    response_data = {
        "profile":{
            "first_name":user.first_name,
            "xp":user.xp,
            "level":user.level,
        },
        "progress": progress_data,
        "recent_notifications": notifications_data,
        "money_saved": total_saved,
        "cigarettes_avoided": cigarettes_avoided,
        "streak_days": streak
    }

    return Response(response_data)
