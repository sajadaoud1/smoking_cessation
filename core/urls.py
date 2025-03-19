from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'smoking-habits',SmokingHabitsView)
router.register(r'quitting-plan', QuittingPlanView)  


urlpatterns = [
    path('',include(router.urls)),
]