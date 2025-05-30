# app.py
from flask import Flask, request
from flask_cors import CORS
from flask_migrate import Migrate
from groq import Groq
from datetime import datetime
from sqlalchemy import func 
import logging
from config import Config
from models import db, Student, Chat
from utils import setup_logging, error_response, success_response, validate_request, get_chat_prompt

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    Migrate(app, db)
    
    # Setup logging
    setup_logging(app)
    
    # Initialize Groq client
    groq_client = Groq(api_key=app.config['GROQ_API_KEY'])

    # Test route to verify API is working
    @app.route('/api/test', methods=['GET'])
    def test_route():
        return success_response({'message': 'API is working!'})
    
    @app.route('/api/start-session', methods=['POST'])
    @validate_request('name', 'email', 'domain')
    def start_session():
        try:
            data = request.json
            student = db.session.query(Student).filter_by(email=data['email']).first()
            
            if student:
                student.last_active = datetime.utcnow()
                student.domain = data['domain']
            else:
                student = Student(
                    name=data['name'],
                    email=data['email'],
                    domain=data['domain']
                )
                db.session.add(student)
            
            db.session.commit()
            return success_response(
                student.to_dict(),
                f'Welcome {student.name}! Ask me anything about {student.domain}.'
            )
            
        except Exception as e:
            app.logger.error(f'Session start error: {str(e)}')
            return error_response('Failed to start session', 500)


    @app.route('/api/chat', methods=['POST'])
    @validate_request('student_id', 'query')  # Remove session_id from required fields
    def chat():
        try:
            data = request.json
            student = db.session.get(Student, data['student_id'])
            if not student:
                return error_response('Student not found', 404)
            
            # Generate session_id if not provided
            session_id = data.get('session_id')
            if not session_id:
                session_id = f"session_{student.id}_{int(datetime.utcnow().timestamp())}"
            
            is_first_message = data.get('is_first_message', False)
            
            # Get Groq response
            groq_key = app.config.get('GROQ_API_KEY')
            groq_client = Groq(api_key=groq_key, timeout=30.0)
            prompt = get_chat_prompt(student.domain, data['query'])
            
            chat_response = groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": data['query']}
                ],
                temperature=0.4,
                max_tokens=1024
            )
            
            response = chat_response.choices[0].message.content
            
            # Create chat entry
            chat = Chat(
                student_id=student.id,
                session_id=session_id,  # Now this will never be None
                query=data['query'],
                response=response,
                is_first_message=is_first_message,
                chat_metadata={
                    'domain': student.domain,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            db.session.add(chat)
            db.session.commit()
            
            return success_response({
                'response': response,
                'chat_id': chat.id,
                'session_id': session_id  # Return the session_id
            })
                
        except Exception as e:
            app.logger.error(f'Chat error: {str(e)}')
            return error_response(str(e), 500)

    @app.route('/api/student/sessions/<int:student_id>', methods=['GET'])
    def get_student_sessions(student_id):
        """Get all chat sessions for a student with their first messages"""
        try:
            student = db.session.get(Student, student_id)
            if not student:
                return error_response('Student not found', 404)
            
            # Get all messages for grouping
            sessions = db.session.query(
                Chat.session_id,
                func.min(Chat.query).label('first_message'),
                func.min(Chat.timestamp).label('created_at'),
                func.max(Chat.timestamp).label('last_activity'),
                func.count(Chat.id).label('message_count')
            ).filter(
                Chat.student_id == student_id
            ).group_by(
                Chat.session_id
            ).order_by(
                func.max(Chat.timestamp).desc()
            ).all()
            
            return success_response({
                'sessions': [{
                    'session_id': session.session_id,
                    'first_message': session.first_message,
                    'created_at': session.created_at.isoformat(),
                    'last_activity': session.last_activity.isoformat(),
                    'message_count': session.message_count
                } for session in sessions],
                'total_sessions': len(sessions)
            })
                
        except Exception as e:
            app.logger.error(f'Session retrieval error: {str(e)}')
            return error_response('Failed to retrieve sessions', 500)    


    # app.py - Backend Fix

    @app.route('/api/chat-history/<int:student_id>', methods=['GET'])
    def get_chat_history(student_id):
        """Get chat history for a specific session"""
        try:
            student = db.session.get(Student, student_id)
            if not student:
                return error_response('Student not found', 404)
            
            session_id = request.args.get('session_id')
            if not session_id:
                return error_response('Session ID required', 400)
            
            # Get all messages for the session in chronological order
            chats = db.session.query(Chat).filter(
                Chat.student_id == student_id,
                Chat.session_id == session_id
            ).order_by(
                Chat.timestamp
            ).all()
            
            if not chats:
                return error_response('Session not found', 404)
            
            # Transform to include both query and response
            messages = []
            for chat in chats:
                messages.extend([
                    {
                        'type': 'user',
                        'content': chat.query,
                        'timestamp': chat.timestamp.isoformat(),
                        'id': f"user_{chat.id}"
                    },
                    {
                        'type': 'bot',
                        'content': chat.response,
                        'timestamp': chat.timestamp.isoformat(),
                        'id': chat.id,
                        'helpful': chat.helpful
                    }
                ])
            
            return success_response({
                'session_id': session_id,
                'messages': messages
            })
                
        except Exception as e:
            app.logger.error(f'Chat history error: {str(e)}')
            return error_response('Failed to retrieve chat history', 500)

    @app.route('/api/feedback', methods=['POST'])
    @validate_request('chat_id', 'helpful')
    def submit_feedback():
        """Submit feedback for a chat response"""
        try:
            app.logger.info('Processing feedback submission')
            data = request.json
            chat = db.session.get(Chat, data['chat_id'])
            
            if not chat:
                return error_response('Chat not found', 404)
            
            chat.helpful = data['helpful']
            db.session.commit()
            
            app.logger.info(f'Successfully submitted feedback for chat {chat.id}')
            return success_response(
                {'chat_id': chat.id},
                'Feedback submitted successfully'
            )
            
        except Exception as e:
            app.logger.error(f'Feedback submission error: {str(e)}')
            return error_response('Failed to submit feedback', 500)

    @app.errorhandler(404)
    def not_found_error(error):
        return error_response('Resource not found', 404)

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return error_response('Internal server error', 500)

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)