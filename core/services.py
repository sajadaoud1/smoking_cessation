from datetime import date
from .models import QuittingPlan
from django.utils import timezone

def gradual_reduction_schedule(cigs_per_day,reduction_day=30):
    """Generates a stepwise reduction plan for gradual quitting."""
    schedule =[]
    step = max(1, round(cigs_per_day/(reduction_day//3)))
    current = cigs_per_day
    while current > 0:
        schedule.append(current)
        current = max(0,current - step)
    return schedule

def assign_quitting_plan(user,duration):
    quitting_plan = QuittingPlan.objects.filter(user=user).first()

    if not quitting_plan or not quitting_plan.smoking_habits:
        return "no smoking habits found, cannot assign a plan."
    
    smoking_habits = quitting_plan.smoking_habits
    cigs_per_day = smoking_habits.cigs_per_day
    
    plan_type = "gradual plan" if cigs_per_day > 10 else "cold_turkey plan"

    quitting_plan.plan_type = plan_type
    quitting_plan.duration = int(duration)
    quitting_plan.start_date = timezone.now()
    quitting_plan.remaining_cigarettes = cigs_per_day
    quitting_plan.save()

    return quitting_plan

def get_motivation_message(user):
    quitting_plan = QuittingPlan.objects.filter(user=user).first()

    # Gradual Reduction Plan Messages
    if quitting_plan:
        today = date.today()
        quit_date = quitting_plan.quit_date
        remaining_cigarettes = quitting_plan.remaining_cigarettes
        plan_type = quitting_plan.plan_type

        if plan_type == "gradual plan":
            if today < quit_date:
                return f"You're doing great! Keep reducing your cigarettes. {remaining_cigarettes} cigarettes left today."
            elif today == quit_date:
                return "Final day of reduction! Prepare for a smoke-free life! "
            else:
                days_since_quit = (today - quit_date).days
                return f"You've completed your reduction plan!  {days_since_quit} days smoke-free!"
        elif plan_type == "cold_turkey plan":
            if today < quit_date:
                return "Get ready! Your quit date is coming up. Stay strong! "
            elif today == quit_date:
                return "Today is your quit day! You've got this! "
            else:
                days_since_quit = (today - quit_date).days
                return f"You're {days_since_quit} days smoke-free! Keep going! "

    return "Set your quit date and start your journey to a healthier life! "
