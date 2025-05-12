from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'users', CustomUserView, basename='users')
router.register(r'smoking-habits', SmokingHabitsView, basename='smoking-habits')
router.register(r'smoking-logs', DailySmokingLogView, basename='smoking-logs')
router.register(r'quitting-plan', QuittingPlanView, basename='quitting-plan')
router.register(r'user-progress', UserProgressView, basename='user-progress')
router.register(r'achievements', AchievementView, basename='achievements')
router.register(r'badge', BadgeView, basename='badge')
router.register(r'reminder', ReminderView, basename='reminder')
router.register(r'chatbot', ChatbotInteractionView, basename='chatbot')
router.register(r'notification', NotificationView, basename='notification')
router.register(r'daily-smoking-log', DailySmokingLogView, basename='daily-smoking-log')

urlpatterns = [
    path('', include(router.urls)),
    path("complete_goal/<int:user_id>/<str:goal_name>/", complete_goal, name="complete_goal"),
    path('dashboard/', dashboard_summary, name='dashboard-summary'),
    path('achievements_and_badges/', achievements_and_badges, name='achievements_and_badges'),
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
