import os
from datetime import datetime
from app import create_app
from app.models import db, User, Subject, Topic, Question

def seed_data():
    app = create_app()
    with app.app_context():
        # 1. Create a default student user if not exists
        default_user = User.query.filter_by(username='java_student').first()
        if not default_user:
            default_user = User(
                username='java_student',
                email='student@studyforge.edu',
                xp=120, # start with some initial XP to show progress
                streak_count=2,
                longest_streak=2,
                last_active_date=datetime.utcnow().date()
            )
            default_user.set_password('studyforge123')
            db.session.add(default_user)
            db.session.commit()
            print("Default student account 'java_student' / 'studyforge123' created!")
        
        # 2. Add 'Core Java' Subject
        subject = Subject.query.filter_by(name='Core Java', user_id=default_user.id).first()
        if not subject:
            subject = Subject(name='Core Java', user_id=default_user.id)
            db.session.add(subject)
            db.session.commit()
            print("Subject 'Core Java' added.")

        # 3. Define Topics & Questions map
        data_map = {
            "Basics": [
                {
                    "q": "What are static blocks and static initializers in Java?",
                    "a": "Static blocks are code blocks that are executed exactly once when the class is loaded into memory, even before the constructors are executed. They are primarily used to initialize static fields."
                },
                {
                    "q": "Why is Java platform independent?",
                    "a": "Java code is compiled into bytecode (.class files), which is platform-neutral. The Java Virtual Machine (JVM) on any specific operating system interprets this bytecode into native machine instructions, making Java platform independent."
                },
                {
                    "q": "Difference between method overloading and method overriding in Java?",
                    "a": "Overloading occurs within the same class where methods have the same name but different parameter signatures (static polymorphism). Overriding occurs between a superclass and subclass where a method has the exact same name, return type, and parameter signature (dynamic polymorphism)."
                }
            ],
            "Exceptions": [
                {
                    "q": "What is the difference between checked and unchecked exceptions?",
                    "a": "Checked exceptions are subclasses of Exception (excluding RuntimeException) and must be handled or declared (using throws) at compile time. Unchecked exceptions are subclasses of RuntimeException and are not checked at compile time."
                },
                {
                    "q": "What is the importance of the finally block in exception handling?",
                    "a": "The finally block is used for clean-up tasks (like closing database connections or files). It is guaranteed to execute, whether an exception is thrown or caught, and even if a return statement is present inside try or catch."
                }
            ],
            "Multithreading": [
                {
                    "q": "What is the difference between yield(), sleep(), and join() methods?",
                    "a": "yield() pauses the current thread to give other threads of equal priority a chance to run; sleep(ms) makes the current thread sleep for a specified duration without releasing locks; join() makes the calling thread wait for the target thread to die."
                },
                {
                    "q": "What are daemon threads in Java?",
                    "a": "Daemon threads are low-priority service threads that run in the background (like the Garbage Collector). The JVM will terminate automatically when all user threads finish executing, even if daemon threads are still running."
                }
            ],
            "Collections": [
                {
                    "q": "What is the difference between HashMap and Hashtable?",
                    "a": "HashMap is not synchronized (not thread-safe), allows one null key and multiple null values, and is faster. Hashtable is synchronized (thread-safe), does not allow null keys or values, and is a legacy class."
                },
                {
                    "q": "When should we use HashSet over TreeSet?",
                    "a": "Use HashSet when you need quick search, insertion, and deletion operations (constant O(1) time complexity) and do not care about the order of elements. Use TreeSet when elements need to be stored in a sorted order (logarithmic O(log n) complexity)."
                }
            ],
            "Serialization": [
                {
                    "q": "What is the role of the transient keyword in Java Serialization?",
                    "a": "The transient keyword is used on fields that should not be serialized. During serialization, the state of transient variables is skipped, and they are restored with default values (null for references, 0/false for primitives) during deserialization."
                }
            ]
        }

        # 4. Insert topics and questions
        for topic_name, q_list in data_map.items():
            topic = Topic.query.filter_by(name=topic_name, subject_id=subject.id).first()
            if not topic:
                topic = Topic(name=topic_name, subject_id=subject.id)
                db.session.add(topic)
                db.session.commit()
                print(f"Topic '{topic_name}' added.")
                
            for q_data in q_list:
                existing_q = Question.query.filter_by(topic_id=topic.id, question_text=q_data["q"]).first()
                if not existing_q:
                    q = Question(
                        topic_id=topic.id,
                        question_text=q_data["q"],
                        answer_text=q_data["a"]
                    )
                    db.session.add(q)
            db.session.commit()
            print(f"Questions seeded for topic '{topic_name}'.")

        print("Database successfully seeded with Core Java interview questions!")

if __name__ == '__main__':
    seed_data()
