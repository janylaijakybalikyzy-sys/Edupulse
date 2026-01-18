from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)  # Сабактын аты (мис: Математика)
    teacher_name = Column(String)      # Мугалимдин аты
    feedbacks = relationship("Feedback", back_populates="subject")

class Feedback(Base):
    __tablename__ = "feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id")) # Кайсы сабакка тиешелүү?
    rating = Column(Integer)
    difficulty = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    subject = relationship("Subject", back_populates="feedbacks")