from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Subject(Base):
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)  # Бул жерден unique=True алып салынды, ар бир сабак жаңы ID алат
    teacher_name = Column(String)
    topic_name = Column(String)
    lesson_date = Column(String)
    
    # Сабак менен пикирлердин байланышы
    feedbacks = relationship("Feedback", back_populates="subject")

class Feedback(Base):
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    rating = Column(Integer)
    difficulty = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Пикир менен сабактын байланышы
    subject = relationship("Subject", back_populates="feedbacks")