from datetime import date,timedelta
from .models import *
from django.utils import timezone

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

def assign_quitting_plan(user):
    quitting_plan = QuittingPlan.objects.filter(user=user).first()

    if not quitting_plan or not quitting_plan.smoking_habits:
        return "no smoking habits found, cannot assign a plan."
    
    smoking_habits:SmokingHabits = quitting_plan.smoking_habits
    cigs_per_day = smoking_habits.cigs_per_day
    
    weeks = 4

    if cigs_per_day > 10:
        plan_type = "Gradual Reduction"
        schedule = generate_weekly_reduction_schedule(cigs_per_day,weeks)
    else:
        plan_type = "Cold Turkey"  
        schedule = [{"week": i + 1, "target_per_day": 0} for i in range(weeks)]

    quitting_plan.plan_type = plan_type
    quitting_plan.duration = weeks*7
    quitting_plan.start_date = timezone.now()
    quitting_plan.remaining_cigarettes = cigs_per_day
    quitting_plan.save()

    response_data={
        "plan_type": plan_type,
        "start_date": quitting_plan.start_date,
        "quit_date": quitting_plan.start_date + timedelta(days=quitting_plan.duration),
        "duration_days": weeks * 7,
    }

    return response_data

def get_motivation_message(user):
    quitting_plan = QuittingPlan.objects.filter(user=user).first()

    # Gradual Reduction Plan Messages
    if quitting_plan:
        today = date.today()
        quit_date = quitting_plan.quit_date
        remaining_cigarettes = quitting_plan.remaining_cigarettes
        plan_type = quitting_plan.plan_type

        if plan_type == "Gradual Reduction":
            if today < quit_date:
                return f"You're doing great! Keep reducing your cigarettes. {remaining_cigarettes} cigarettes left today."
            elif today == quit_date:
                return "Final day of reduction! Prepare for a smoke-free life! "
            else:
                days_since_quit = (today - quit_date).days
                return f"You've completed your reduction plan!  {days_since_quit} days smoke-free!"
        elif plan_type == "Cold Turkey":
            if today < quit_date:
                return "Get ready! Your quit date is coming up. Stay strong! "
            elif today == quit_date:
                return "Today is your quit day! You've got this! "
            else:
                days_since_quit = (today - quit_date).days
                return f"You're {days_since_quit} days smoke-free! Keep going! "

    return "Set your quit date and start your journey to a healthier life! "

def log_cigarette(user,count):
    plan = QuittingPlan.objects.filter(user=user).first()
    if plan:
        plan.remaining_cigarettes = max(0, plan.remaining_cigarettes - count)
        plan.save()

def calculate_cigarettes_avoided(user):
    plan = QuittingPlan.objects.filter(user=user).first()
    if not plan or not plan.smoking_habits:
        return 0

    original_cigs = plan.smoking_habits.cigs_per_day
    schedule = generate_weekly_reduction_schedule(original_cigs)

    today = date.today()
    days_since_start = (today - plan.start_date).days

    total_avoided = 0

    for day in range(days_since_start + 1):
        week = min((day// 7) + 1, len(schedule))
        target_per_day = next((item["target_per_day"] for item in schedule if item["week"] == week),original_cigs)
        avoided = original_cigs - target_per_day
        total_avoided += avoided

    return total_avoided