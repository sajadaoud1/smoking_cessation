from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'smoking-habits',SmokingHabitsView,basename='smoking-habits')
router.register(r'quitting-plan', QuittingPlanView,basename='quitting-plan')  
router.register(r'user-progress',UserProgressView,basename='user-progress')
router.register(r'achievements', AchievementView, basename='achievements')
router.register(r'reminder', ReminderView, basename='reminder')
router.register(r'chatbot', ChatbotInteractionView, basename='chatbot')
router.register(r'badge', ChatbotInteractionView, basename='badge')
router.register(r'notification', ChatbotInteractionView, basename='notification')

urlpatterns = [
    path('',include(router.urls)),
]