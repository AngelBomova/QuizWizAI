import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

# Global variables for engine and session
engine = None
SessionLocal = None

class QuizHistory(Base):
    __tablename__ = "quiz_history"
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    num_questions = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)
    percentage = Column(Float, nullable=False)
    quiz_data = Column(Text, nullable=True)  # Store quiz questions/answers as JSON
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
def init_db():
    global engine, SessionLocal
    
    # Get database URL from environment
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set. Please ensure the PostgreSQL database is configured.")
    
    # Create SQLAlchemy engine
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)

# Get database session
def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

# Save quiz result
def save_quiz_result(topic: str, difficulty: str, num_questions: int, score: int, percentage: float, quiz_data: str = None):
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    db = SessionLocal()
    try:
        quiz_record = QuizHistory(
            topic=topic,
            difficulty=difficulty,
            num_questions=num_questions,
            score=score,
            percentage=percentage,
            quiz_data=quiz_data
        )
        db.add(quiz_record)
        db.commit()
        db.refresh(quiz_record)
        return quiz_record
    finally:
        db.close()

# Get quiz history
def get_quiz_history(limit: int = 10):
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    db = SessionLocal()
    try:
        history = db.query(QuizHistory).order_by(QuizHistory.created_at.desc()).limit(limit).all()
        return history
    finally:
        db.close()

# Get statistics
def get_quiz_statistics():
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    
    db = SessionLocal()
    try:
        total_quizzes = db.query(QuizHistory).count()
        if total_quizzes == 0:
            return {
                "total_quizzes": 0,
                "average_score": 0,
                "best_score": 0,
                "total_questions_answered": 0
            }
        
        avg_percentage = db.query(QuizHistory).with_entities(
            QuizHistory.percentage
        ).all()
        
        avg_score = sum([p[0] for p in avg_percentage]) / len(avg_percentage) if avg_percentage else 0
        best_score = max([p[0] for p in avg_percentage]) if avg_percentage else 0
        
        total_questions = db.query(QuizHistory).with_entities(
            QuizHistory.num_questions
        ).all()
        total_questions_answered = sum([q[0] for q in total_questions])
        
        return {
            "total_quizzes": total_quizzes,
            "average_score": round(avg_score, 1),
            "best_score": round(best_score, 1),
            "total_questions_answered": total_questions_answered
        }
    finally:
        db.close()
