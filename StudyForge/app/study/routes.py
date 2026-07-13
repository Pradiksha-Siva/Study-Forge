from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import db, Question, StudyLog, Achievement, UserAchievement, Topic, Subject

study = Blueprint('study', __name__)

@study.route('/session')
@login_required
def session():
    # Render study page
    return render_template('study/session.html')

@study.route('/due-cards', methods=['GET'])
@login_required
def due_cards():
    mode = request.args.get('mode', 'due') # 'due' or 'practice'
    
    # Query questions belonging to the current user
    query = Question.query.join(Topic).join(Subject).filter(Subject.user_id == current_user.id)
    
    if mode == 'due':
        # Get cards scheduled for review now or in the past
        questions = query.filter(Question.next_review <= datetime.utcnow()).all()
    else:
        # Practice mode gets all cards
        questions = query.all()
        
    cards_data = []
    for q in questions:
        cards_data.append({
            "id": q.id,
            "subject": q.topic.subject.name,
            "topic": q.topic.name,
            "question": q.question_text,
            "answer": q.answer_text,
            "ease_factor": q.ease_factor,
            "interval": q.interval,
            "repetitions": q.repetitions
        })
        
    return jsonify({"cards": cards_data, "mode": mode})

@study.route('/rate/<int:q_id>', methods=['POST'])
@login_required
def rate_card(q_id):
    q = Question.query.get_or_404(q_id)
    if q.topic.subject.user_id != current_user.id:
        return jsonify({"success": False, "error": "Unauthorized"}), 403
        
    data = request.get_json() or {}
    rating = data.get('rating') # Forgot, Hard, Medium, Easy
    if rating not in ['Forgot', 'Hard', 'Medium', 'Easy']:
        return jsonify({"success": False, "error": "Invalid rating"}), 400
        
    # Apply SM-2 Spaced Repetition logic
    if rating == 'Easy':
        q_val = 5
        xp_gain = 15
    elif rating == 'Medium':
        q_val = 4
        xp_gain = 10
    elif rating == 'Hard':
        q_val = 2
        xp_gain = 5
    else: # Forgot
        q_val = 0
        xp_gain = 2
        
    # Calculate Ease Factor
    q.ease_factor = q.ease_factor + (0.1 - (5 - q_val) * (0.08 + (5 - q_val) * 0.02))
    if q.ease_factor < 1.3:
        q.ease_factor = 1.3
        
    # Calculate Interval and Repetitions
    if q_val < 3: # Reset repetitions and set interval to 1 day
        q.repetitions = 0
        q.interval = 1
    else:
        if q.repetitions == 0:
            q.interval = 1
        elif q.repetitions == 1:
            q.interval = 6
        else:
            q.interval = int(round(q.interval * q.ease_factor))
        q.repetitions += 1
        
    q.next_review = datetime.utcnow() + timedelta(days=q.interval)
    
    # Save Study Log
    log = StudyLog(user_id=current_user.id, question_id=q.id, rating=rating, xp_gained=xp_gain)
    db.session.add(log)
    
    # Update User XP
    current_user.xp += xp_gain
    
    # Update User Streak
    today = date.today()
    last_active = current_user.last_active_date
    
    if last_active is None:
        current_user.streak_count = 1
    elif last_active == today - timedelta(days=1):
        current_user.streak_count += 1
    elif last_active < today - timedelta(days=1):
        current_user.streak_count = 1
    # If last_active == today, streak remains unchanged
    
    current_user.last_active_date = today
    
    # Update Longest Streak
    if current_user.streak_count > current_user.longest_streak:
        current_user.longest_streak = current_user.streak_count
        
    # Check Achievements Progressions
    unlocked = check_achievements()
    
    db.session.commit()
    
    return jsonify({
        "success": True,
        "xp_gained": xp_gain,
        "total_xp": current_user.xp,
        "level": current_user.level,
        "xp_in_level": current_user.xp_in_level,
        "streak": current_user.streak_count,
        "unlocked_achievements": unlocked
    })

def check_achievements():
    unlocked_list = []
    
    # 1. Total questions answered
    total_answered = StudyLog.query.filter_by(user_id=current_user.id).count()
    
    # 2. XP total
    xp_total = current_user.xp
    
    # 3. Streak
    streak = current_user.streak_count
    
    # Query all achievements
    achievements = Achievement.query.all()
    for ach in achievements:
        # Check if already unlocked
        already_unlocked = UserAchievement.query.filter_by(user_id=current_user.id, achievement_id=ach.id).first()
        if already_unlocked:
            continue
            
        unlocked_now = False
        if ach.type == 'questions_answered' and total_answered >= ach.threshold:
            unlocked_now = True
        elif ach.type == 'xp' and xp_total >= ach.threshold:
            unlocked_now = True
        elif ach.type == 'streak' and streak >= ach.threshold:
            unlocked_now = True
            
        if unlocked_now:
            ua = UserAchievement(user_id=current_user.id, achievement_id=ach.id)
            db.session.add(ua)
            unlocked_list.append({
                "name": ach.name,
                "description": ach.description,
                "badge_icon": ach.badge_icon
            })
            
    return unlocked_list
