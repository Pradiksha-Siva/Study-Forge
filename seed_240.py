import json
import os
from app import create_app
from app.models import db, User, Subject, Topic, Question

app = create_app()

with app.app_context():
    # Load JSON
    base_dir = os.path.abspath(os.path.dirname(__file__))
    json_path = os.path.join(base_dir, 'scratch', 'extracted_questions.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        questions_data = json.load(f)
        
    print(f"Loaded {len(questions_data)} questions from JSON.")
    
    # Need a user to assign the subject to
    user = User.query.first()
    if not user:
        user = User(username='testuser', email='test@test.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        print("Created test user.")
        
    # Create Subject
    subject = Subject.query.filter_by(name='Java Core', user_id=user.id).first()
    if not subject:
        subject = Subject(name='Java Core', user_id=user.id)
        db.session.add(subject)
        db.session.commit()
        print("Created Java Core subject.")
        
    # Create Topic
    topic = Topic.query.filter_by(name='General Questions', subject_id=subject.id).first()
    if not topic:
        topic = Topic(name='General Questions', subject_id=subject.id)
        db.session.add(topic)
        db.session.commit()
        print("Created General Questions topic.")
        
    # Add Questions
    added_count = 0
    for q_data in questions_data:
        # Check if question already exists to avoid duplicates
        existing = Question.query.filter_by(topic_id=topic.id, question_text=q_data['question']).first()
        if not existing:
            q = Question(
                topic_id=topic.id,
                question_text=q_data['question'],
                answer_text=q_data['answer']
            )
            db.session.add(q)
            added_count += 1
            
    db.session.commit()
    print(f"Successfully added {added_count} new questions to the database.")
    
    total = Question.query.count()
    print(f"Total questions in database: {total}")
