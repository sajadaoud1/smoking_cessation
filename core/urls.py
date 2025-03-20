from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'smoking-habits',SmokingHabitsView,basename='smoking-habits')
router.register(r'quitting-plan', QuittingPlanView,basename='quitting-plan')  
router.register(r'user-progress',UserProgressView,basename='user-progress')
router.register(r'achievements', AchievementView, basename='achievements')


urlpatterns = [
    path('',include(router.urls)),
]