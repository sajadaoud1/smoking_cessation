from celery import shared_task
from django.utils import timezone
from core.models import CustomUser, Notification
from utils.notification import send_push_notification

@shared_task(name="send_daily_checkin_notifications")
def send_daily_checkin_notifications():
    print("Sending daily check-in notification in 9 PM")
    users = CustomUser.objects.exclude(fcm_token_isnull=True).exclude(fcm_token_exact="")
    for user in users:
        Notification.objects.create(
            user=user,
            title="Daily Check-In",
            message="It's 9 PM! Time to log your smoking habits."
        )
        send_push_notification(
            registration_token=user.fcm_token,
            title="Daily Check-In",
            body="It's 9 PM! Time to log your smoking habits."
        )