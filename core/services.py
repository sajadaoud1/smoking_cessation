from datetime import date,timedelta
from .models import *
from django.utils import timezone
from core.utils.notification import send_push_notification
from core.utils.exchange import fetch_exchange_rates
def generate_weekly_reduction_schedule(cigs_per_day, min_cigs=2):
    schedule =[]
    original = cigs_per_day
    reduction_step = original * 0.2
    week = 1

    while True:
        target = round(original - (reduction_step * (week - 1)))
        if target <= min_cigs:
            break
        schedule.append({
            "week":week,
            "target_per_day":target
        })
        week += 1

    schedule.append({
            "week":week,
            "target_per_day":0
        })

    return schedule

def assign_quitting_plan(user:CustomUser):
    quitting_plan = QuittingPlan.objects.filter(user=user).first()

    if not quitting_plan or not quitting_plan.smoking_habits:
        return "no smoking habits found, cannot assign a plan."
    
    smoking_habits:SmokingHabits = quitting_plan.smoking_habits
    cigs_per_day = smoking_habits.cigs_per_day
    years_smoking = user.years_of_smoking  or 0
    
    if cigs_per_day > 10 and years_smoking >=10:
        plan_type = "Gradual Reduction"
        schedule = generate_weekly_reduction_schedule(cigs_per_day,min_cigs=2)
        duration_days = len(schedule) * 7
    else:
        plan_type = "Cold Turkey"  
        schedule = [{"week": i + 1, "target_per_day": 0} for i in range(4)]
        duration_days = 28

    quitting_plan.plan_type = plan_type
    quitting_plan.duration = duration_days
    quitting_plan.start_date = timezone.now()
    quitting_plan.save()

    response_data={
        "plan_type": plan_type,
        "start_date": quitting_plan.start_date,
        "quit_date": quitting_plan.start_date + timedelta(days=duration_days),
        "duration_days": duration_days,
        "years_smoking":years_smoking,
    }

    return response_data

def get_target_for_today(user):
    try:
        plan = QuittingPlan.objects.get(user=user)
    except QuittingPlan.DoesNotExist:
        return 0
        
    day_passed = (timezone.now().date() - plan.start_date).days
    
    if day_passed < 0:
        return 0
    
    week_number = day_passed // 7 + 1
    smoking_habits :SmokingHabits = plan.smoking_habits
    schedule = generate_weekly_reduction_schedule(smoking_habits.cigs_per_day)
    for week_plan in schedule:
        if week_plan['week'] == week_number:
            return week_plan['target_per_day']
    return schedule[-1]['target_per_day']

def check_achievements_and_award_badges(user:CustomUser):
    progress = UserProgress.objects.filter(user=user).first()
    if not progress:
        return
    
    cigarettes_avoided = progress.cigarettes_avoided

    milestones = [
        (20,"Avoided 20 Cigarettes","You've avoided 20 cigarettes!","Consistent Challenger"),
        (50,"Avoided 50 Cigarettes","You've avoided 50 cigarettes!","Bronze Quitter"),
        (100,"Avoided 100 Cigarettes","You've avoided 100 cigarettes!","Selver Quitter"),
        (150,"Avoided 150 Cigarettes","You've avoided 150 cigarettes!","Gold Achiever"),
        (200,"Avoided 200 Cigarettes","You've avoided 200 cigarettes!","legendary achiever"),
    ]

    image_paths = {
    "Consistent Challenger": "badges/level_1_badge.jpeg",
    "Bronze Quitter": "badges/level_2_badge.jpeg",
    "Selver Quitter": "badges/level_3_badge.jpeg",
    "Gold Achiever": "badges/level_4_badge.jpeg",
    "legendary achiever": "badges/level_5_badge.jpeg",
    }

    for threshold,ach_name,ach_desc,badge_name in milestones:
        if cigarettes_avoided >= threshold:
            achievement  , created = Achievement.objects.get_or_create(
                name=ach_name,
                defaults={
                    "description": ach_desc,
                    "date_earned": timezone.now(),
                }
            )
            if not user.achievements.filter(id = achievement.id).exists():
                user.achievements.add(achievement)
                badge, _ = Badge.objects.get_or_create(name=badge_name,defaults={
                    "description":f"Earned for avoiding {threshold} cigarettes",
                    "icon":image_paths.get(badge_name)
                    })
                user.badges.add(badge)

                if user.fcm_token and user.fcm_token.strip():
                    send_push_notification(
                        user.fcm_token,
                        title="Congratulations!",
                        body=f"You unlocked '{achievement.name}' and earned the '{badge.name}' badge!"
                    )
                Notification.objects.create(
                    user=user,
                    title="Achievement Unlocked",
                    message=f"You unlocked '{achievement.name}' and earned the '{badge.name}' badge " 
                )
    user.save()

    print(f"checking achievements for {user.username} with {cigarettes_avoided} avoided")

def update_user_progress(user):
    avoided = calculate_cigarettes_avoided(user)
    day_quit = calculate_days_quit(user)
    progress, _ = UserProgress.objects.get_or_create(user=user)
    progress.cigarettes_avoided = avoided
    progress.days_without_smoking = day_quit
    progress.save()

    check_achievements_and_award_badges(user)

def calculate_cigarettes_avoided(user):
    plan = QuittingPlan.objects.filter(user=user).first()
    if not plan or not plan.smoking_habits:
        return 0

    original_cigs = plan.smoking_habits.cigs_per_day
    schedule = generate_weekly_reduction_schedule(original_cigs)

    logs = DailySmokingLog.objects.filter(user=user, date__gte=plan.start_date)

    total_avoided = 0

    for log in logs:
        days_passed = (log.date - plan.start_date).days
        week_number = min((days_passed // 7) + 1, len(schedule))
        target = next((item["target_per_day"] for item in schedule if item["week"] == week_number),original_cigs)
        actual = log.cigarettes_smoked

        if actual < target:
            total_avoided += (target - log.cigarettes_smoked)

    return total_avoided

def calculate_money_saved(user, target_currency=None):

    plan = QuittingPlan.objects.filter(user=user).first()
    if not plan or not plan.smoking_habits:
        return {"money_saved": 0.0, "currency": "JOD"}

    smoking_habits: SmokingHabits = plan.smoking_habits
    cigs_per_day = smoking_habits.cigs_per_day
    cig_per_pack = smoking_habits.cigs_per_pack
    pack_cost = float(smoking_habits.pack_cost)
    base_currency = "JOD"
    preferred_currency = target_currency or smoking_habits.currency or base_currency

    cost_per_cig = pack_cost / cig_per_pack

    logs = DailySmokingLog.objects.filter(user=user, date__gte=plan.start_date)
    total_saved_jod = sum(max(0, cigs_per_day - log.cigarettes_smoked) * cost_per_cig for log in logs)
    total_saved_jod = round(total_saved_jod, 2)

    if preferred_currency == base_currency:
        return {"money_saved": total_saved_jod, "currency": base_currency}

    rates = fetch_exchange_rates(base_currency)

    if isinstance(rates, dict):
        rate = rates.get(preferred_currency.upper())

        if rate:
            converted = round(total_saved_jod * rate, 2)
            return {
                "money_saved": converted,
                "currency": preferred_currency.upper()
            }

    return {
        "money_saved": total_saved_jod,
        "currency": base_currency
    }

def calculate_days_quit(user):
    plan = QuittingPlan.objects.filter(user=user).first()
    if not plan:
        return 0
    logs = DailySmokingLog.objects.filter(user=user, date__gte=plan.start_date)
    days_quit = logs.filter(cigarettes_smoked=0).count()
    return days_quit