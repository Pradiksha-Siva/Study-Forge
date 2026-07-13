import random
from datetime import datetime, date, time, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from app.models import db, User, StudyLog, Achievement, UserAchievement, Question, Topic, Subject

main = Blueprint('main', __name__)

MOTIVATIONAL_QUOTES = [
    "Craft Consistency. Forge Excellence.",
    "The secret of getting ahead is getting started. - Mark Twain",
    "It always seems impossible until it's done. - Nelson Mandela",
    "Don't wish it were easier. Wish you were better. - Jim Rohn",
    "There are no shortcuts to any place worth going. - Beverly Sills",
    "Consistency is what transforms average into excellence.",
    "Small daily improvements over time lead to stunning results. - Robin Sharma",
    "Focus on progress, not perfection.",
    "The only limit to our realization of tomorrow is our doubts of today. - Franklin D. Roosevelt",
    "Code is like humor. When you have to explain it, it's bad. - Cory House",
    "First, solve the problem. Then, write the code. - John Johnson"
]

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    # Calculate today's study count
    today_start = datetime.combine(date.today(), time.min)
    today_count = StudyLog.query.filter_by(user_id=current_user.id)\
                               .filter(StudyLog.timestamp >= today_start).count()
                               
    # Get daily motivational quote
    quote_index = date.today().timetuple().tm_yday % len(MOTIVATIONAL_QUOTES)
    quote = MOTIVATIONAL_QUOTES[quote_index]
    
    # Get user's unlocked achievements mapping
    unlocked_ach_ids = [ua.achievement_id for ua in UserAchievement.query.filter_by(user_id=current_user.id).all()]
    all_achievements = Achievement.query.all()
    
    # Get total questions reviewed
    total_reviews = StudyLog.query.filter_by(user_id=current_user.id).count()
    
    # Total cards in deck
    total_cards = Question.query.join(Topic).join(Subject).filter(Subject.user_id == current_user.id).count()
    
    # Cards due today
    due_cards_count = Question.query.join(Topic).join(Subject)\
                                   .filter(Subject.user_id == current_user.id, Question.next_review <= datetime.utcnow()).count()
    
    return render_template('main/dashboard.html',
                           today_count=today_count,
                           quote=quote,
                           all_achievements=all_achievements,
                           unlocked_ach_ids=unlocked_ach_ids,
                           total_reviews=total_reviews,
                           total_cards=total_cards,
                           due_cards_count=due_cards_count)

@main.route('/update-goal', methods=['POST'])
@login_required
def update_goal():
    goal = request.form.get('daily_goal')
    if goal and goal.isdigit() and int(goal) > 0:
        current_user.daily_goal = int(goal)
        db.session.commit()
        flash('Daily study goal updated!', 'success')
    else:
        flash('Invalid goal number!', 'danger')
    return redirect(request.referrer or url_for('main.dashboard'))

@main.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    # 1. GitHub contribution graph mapping (past 6 months)
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    
    # Fetch logs
    logs = db.session.query(
        func.date(StudyLog.timestamp).label('log_date'),
        func.count(StudyLog.id).label('log_count')
    ).filter(
        StudyLog.user_id == current_user.id,
        StudyLog.timestamp >= six_months_ago
    ).group_by(func.date(StudyLog.timestamp)).all()
    
    calendar_data = {log.log_date: log.log_count for log in logs}
    
    # 2. Weekly review charts (last 7 days)
    weekly_labels = []
    weekly_counts = []
    
    for i in range(6, -1, -1):
        target_date = date.today() - timedelta(days=i)
        target_start = datetime.combine(target_date, time.min)
        target_end = datetime.combine(target_date, time.max)
        
        count = StudyLog.query.filter_by(user_id=current_user.id)\
                             .filter(StudyLog.timestamp.between(target_start, target_end)).count()
                             
        weekly_labels.append(target_date.strftime('%a'))
        weekly_counts.append(count)
        
    # 3. Daily goal tracker
    today_start = datetime.combine(date.today(), time.min)
    today_count = StudyLog.query.filter_by(user_id=current_user.id)\
                               .filter(StudyLog.timestamp >= today_start).count()
                               
    return jsonify({
        "calendar": calendar_data,
        "weekly": {
            "labels": weekly_labels,
            "counts": weekly_counts
        },
        "today_count": today_count,
        "daily_goal": current_user.daily_goal
    })
