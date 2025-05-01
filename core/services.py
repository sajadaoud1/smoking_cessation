from datetime import date
from .models import *
from django.utils import timezone

def generate_weekly_reduction_schedule(cigs_per_day, weeks=4):
    schedule =[]
    current = cigs_per_day
    reduction = max(1,cigs_per_day // weeks)

    for week in range(1, weeks):
        current = max(2, current - reduction)
        schedule.append({"week":week,"target_per_day": current})

    schedule.append({"week":weeks,"target_per_day":0})

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
        plan_type = "cold_turkey"  
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
