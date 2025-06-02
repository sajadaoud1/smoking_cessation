from core.models import CustomUser
from .notification import send_push_notification

def calculate_level(xp:int):
    level = 1
    while xp >= 50 * level * level:
        level += 1
    return level

def award_dynamic_xp(user:CustomUser,earned_xp:int,reason:str):
    user.xp =max(0, user.xp + earned_xp)
    new_level = calculate_level(user.xp)

    if user.fcm_token and user.fcm_token.strip():
        if new_level > user.level:
            send_push_notification(
                registration_token=user.fcm_token,
                title="Level Up!",
                body=f"Awesome, '{user.first_name}' You've reached Level '{new_level}' Keep going!"
            )
        else:
            send_push_notification(
                registration_token=user.fcm_token,
                title="XP Gained!",
                body=f"{reason} You have earned '{earned_xp}' XP, Keep it up!"
        )
    user.level = new_level
    user.save()
