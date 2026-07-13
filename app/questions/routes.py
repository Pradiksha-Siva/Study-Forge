import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, make_response
from flask_login import login_required, current_user
from app.models import db, Subject, Topic, Question

questions = Blueprint('questions', __name__)

@questions.route('/', methods=['GET'])
@login_required
def index():
    search_query = request.args.get('search', '').strip()
    
    # Get subjects for the current user
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    
    filtered_questions = []
    if search_query:
        # Search questions belonging to the user's subjects
        filtered_questions = Question.query.join(Topic).join(Subject).filter(
            Subject.user_id == current_user.id,
            (Question.question_text.like(f'%{search_query}%')) | 
            (Question.answer_text.like(f'%{search_query}%')) |
            (Topic.name.like(f'%{search_query}%')) |
            (Subject.name.like(f'%{search_query}%'))
        ).all()
        
    return render_template('questions/index.html', subjects=subjects, search_query=search_query, filtered_questions=filtered_questions)

@questions.route('/subject/add', methods=['POST'])
@login_required
def add_subject():
    name = request.form.get('name', '').strip()
    if not name:
        flash('Subject name cannot be empty!', 'danger')
        return redirect(url_for('questions.index'))
        
    existing = Subject.query.filter_by(name=name, user_id=current_user.id).first()
    if existing:
        flash('Subject already exists!', 'danger')
        return redirect(url_for('questions.index'))
        
    new_sub = Subject(name=name, user_id=current_user.id)
    db.session.add(new_sub)
    db.session.commit()
    flash(f'Subject "{name}" created!', 'success')
    return redirect(url_for('questions.index'))

@questions.route('/subject/delete/<int:id>', methods=['POST', 'GET'])
@login_required
def delete_subject(id):
    sub = Subject.query.get_or_404(id)
    if sub.user_id != current_user.id:
        flash('Unauthorized action!', 'danger')
        return redirect(url_for('questions.index'))
        
    db.session.delete(sub)
    db.session.commit()
    flash('Subject and all its topics/questions deleted!', 'success')
    return redirect(url_for('questions.index'))

@questions.route('/topic/add', methods=['POST'])
@login_required
def add_topic():
    subject_id = request.form.get('subject_id')
    name = request.form.get('name', '').strip()
    
    if not name or not subject_id:
        flash('Invalid inputs!', 'danger')
        return redirect(url_for('questions.index'))
        
    sub = Subject.query.get_or_404(subject_id)
    if sub.user_id != current_user.id:
        flash('Unauthorized action!', 'danger')
        return redirect(url_for('questions.index'))
        
    existing = Topic.query.filter_by(name=name, subject_id=subject_id).first()
    if existing:
        flash('Topic already exists in this subject!', 'danger')
        return redirect(url_for('questions.index'))
        
    new_topic = Topic(name=name, subject_id=subject_id)
    db.session.add(new_topic)
    db.session.commit()
    flash(f'Topic "{name}" created under {sub.name}!', 'success')
    return redirect(url_for('questions.index'))

@questions.route('/topic/delete/<int:id>', methods=['POST', 'GET'])
@login_required
def delete_topic(id):
    topic = Topic.query.get_or_404(id)
    if topic.subject.user_id != current_user.id:
        flash('Unauthorized action!', 'danger')
        return redirect(url_for('questions.index'))
        
    db.session.delete(topic)
    db.session.commit()
    flash('Topic and all its questions deleted!', 'success')
    return redirect(url_for('questions.index'))

@questions.route('/question/add', methods=['POST'])
@login_required
def add_question():
    topic_id = request.form.get('topic_id')
    question_text = request.form.get('question_text', '').strip()
    answer_text = request.form.get('answer_text', '').strip()
    
    if not topic_id or not question_text or not answer_text:
        flash('All fields are required to create a question!', 'danger')
        return redirect(url_for('questions.index'))
        
    topic = Topic.query.get_or_404(topic_id)
    if topic.subject.user_id != current_user.id:
        flash('Unauthorized action!', 'danger')
        return redirect(url_for('questions.index'))
        
    new_q = Question(topic_id=topic_id, question_text=question_text, answer_text=answer_text)
    db.session.add(new_q)
    db.session.commit()
    flash('Question added to your deck!', 'success')
    return redirect(url_for('questions.index'))

@questions.route('/question/edit/<int:id>', methods=['POST'])
@login_required
def edit_question(id):
    question = Question.query.get_or_404(id)
    if question.topic.subject.user_id != current_user.id:
        flash('Unauthorized action!', 'danger')
        return redirect(url_for('questions.index'))
        
    question_text = request.form.get('question_text', '').strip()
    answer_text = request.form.get('answer_text', '').strip()
    topic_id = request.form.get('topic_id')
    
    if not question_text or not answer_text or not topic_id:
        flash('Question text and Answer text cannot be empty!', 'danger')
        return redirect(url_for('questions.index'))
        
    new_topic = Topic.query.get_or_404(topic_id)
    if new_topic.subject.user_id != current_user.id:
        flash('Unauthorized action!', 'danger')
        return redirect(url_for('questions.index'))
        
    question.question_text = question_text
    question.answer_text = answer_text
    question.topic_id = topic_id
    
    db.session.commit()
    flash('Question updated successfully!', 'success')
    return redirect(url_for('questions.index'))

@questions.route('/question/delete/<int:id>', methods=['POST', 'GET'])
@login_required
def delete_question(id):
    q = Question.query.get_or_404(id)
    if q.topic.subject.user_id != current_user.id:
        flash('Unauthorized action!', 'danger')
        return redirect(url_for('questions.index'))
        
    db.session.delete(q)
    db.session.commit()
    flash('Question removed from deck!', 'success')
    return redirect(url_for('questions.index'))

@questions.route('/export', methods=['GET'])
@login_required
def export_questions():
    # Construct a JSON representing all Subjects, Topics, and Questions of the user
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    export_data = []
    
    for sub in subjects:
        sub_data = {
            "subject": sub.name,
            "topics": []
        }
        for topic in sub.topics:
            topic_data = {
                "topic": topic.name,
                "questions": []
            }
            for q in topic.questions:
                topic_data["questions"].append({
                    "question": q.question_text,
                    "answer": q.answer_text,
                    "ease_factor": q.ease_factor,
                    "interval": q.interval,
                    "repetitions": q.repetitions
                })
            sub_data["topics"].append(topic_data)
        export_data.append(sub_data)
        
    json_string = json.dumps(export_data, indent=4)
    response = make_response(json_string)
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = 'attachment; filename=studyforge_export.json'
    return response

@questions.route('/import', methods=['POST'])
@login_required
def import_questions():
    if 'import_file' not in request.files:
        flash('No file selected!', 'danger')
        return redirect(url_for('questions.index'))
        
    file = request.files['import_file']
    if file.filename == '':
        flash('No file selected!', 'danger')
        return redirect(url_for('questions.index'))
        
    if file and file.filename.endswith('.json'):
        try:
            data = json.load(file)
            imported_count = 0
            
            for sub_entry in data:
                sub_name = sub_entry.get('subject')
                if not sub_name:
                    continue
                # Get or create subject
                subject = Subject.query.filter_by(name=sub_name, user_id=current_user.id).first()
                if not subject:
                    subject = Subject(name=sub_name, user_id=current_user.id)
                    db.session.add(subject)
                    db.session.commit()
                    
                for topic_entry in sub_entry.get('topics', []):
                    topic_name = topic_entry.get('topic')
                    if not topic_name:
                        continue
                    # Get or create topic
                    topic = Topic.query.filter_by(name=topic_name, subject_id=subject.id).first()
                    if not topic:
                        topic = Topic(name=topic_name, subject_id=subject.id)
                        db.session.add(topic)
                        db.session.commit()
                        
                    for q_entry in topic_entry.get('questions', []):
                        q_text = q_entry.get('question')
                        a_text = q_entry.get('answer')
                        if not q_text or not a_text:
                            continue
                            
                        # Add question
                        ease = q_entry.get('ease_factor', 2.5)
                        inter = q_entry.get('interval', 0)
                        rep = q_entry.get('repetitions', 0)
                        
                        # Avoid duplicates in same topic
                        existing_q = Question.query.filter_by(topic_id=topic.id, question_text=q_text).first()
                        if not existing_q:
                            new_q = Question(
                                topic_id=topic.id,
                                question_text=q_text,
                                answer_text=a_text,
                                ease_factor=ease,
                                interval=inter,
                                repetitions=rep
                            )
                            db.session.add(new_q)
                            imported_count += 1
            
            db.session.commit()
            flash(f'Import completed! Successfully imported {imported_count} questions.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to parse JSON file: {str(e)}', 'danger')
    else:
        flash('Invalid file format. Please upload a JSON file.', 'danger')
        
    return redirect(url_for('questions.index'))
