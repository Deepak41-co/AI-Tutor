# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    domain = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    chats = db.relationship('Chat', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'domain': self.domain,
            'created_at': self.created_at.isoformat(),
            'last_active': self.last_active.isoformat()
        }

class Chat(db.Model):
    __tablename__ = 'chats'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    session_id = db.Column(db.String(50), nullable=False)  # Make it required now
    query = db.Column(db.Text, nullable=False)
    code_snippet = db.Column(db.Text, nullable=True)
    response = db.Column(db.Text, nullable=False)
    is_first_message = db.Column(db.Boolean, default=False)  # New column
    chat_metadata = db.Column(JSONB, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    helpful = db.Column(db.Boolean, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'query': self.query,
            'response': self.response,
            'code_snippet': self.code_snippet,
            'chat_metadata': self.chat_metadata,
            'timestamp': self.timestamp.isoformat(),
            'helpful': self.helpful,
            'is_first_message': self.is_first_message
        }
