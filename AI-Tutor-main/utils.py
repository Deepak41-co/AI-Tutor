# utils.py
from functools import wraps
from flask import jsonify, request
import logging
import re

def setup_logging(app):
    """Setup logging configuration"""
    if not app.debug and not app.testing:
        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('AI Tutor startup')
    return app

def error_response(message, status_code=400):
    """Create a error response"""
    return jsonify({
        'status': 'error',
        'message': message
    }), status_code

def success_response(data, message=None):
    """Create a success response"""
    response = {
        'status': 'success',
        'data': data
    }
    if message:
        response['message'] = message
    return jsonify(response)

def validate_request(*required_fields):
    """Validate request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return error_response('Content-Type must be application/json')
            
            data = request.get_json()
            if not data:
                return error_response('No JSON data provided')
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return error_response(f'Missing required fields: {", ".join(missing_fields)}')
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# utils.py

# utils.py

def get_chat_prompt(domain, query):
    base_prompt = (
        f"You are a friendly and expert AI chatbot specialized in {domain} from SUN E-LEARNING edtech company. "
        "Your role is to assist the student effectively while maintaining the context of the conversation. "
        "\n\nCONTEXT MANAGEMENT RULES:"
        "\n1. Always reference previous parts of the conversation when relevant"
        "\n2. When answering follow-up questions, explicitly mention what you're referring to"
        "\n3. If a student uses words like 'it', 'that', 'this', connect them to previously discussed topics"
        "\n4. Build upon concepts previously explained in the conversation"
        "\n5. For sequential questions, maintain continuity in explanations"
        "\n6. If switching topics, acknowledge the transition"
        "\n7. If a concept was already explained, reference it instead of repeating"
        "\n\nAdditionally, adhere strictly to the following guidelines:"
    )

    base_prompt += """
    1. CONTEXT AWARENESS:
    - **Greetings:** Single friendly sentence response, no code
    - **Small talk:** Brief 1-2 sentence reply, no code
    - **Technical questions:** 
        * Reference previous related questions if any
        * Build upon previously explained concepts
        * Mention connections to earlier topics
        * Provide examples that relate to previous examples
    - **Follow-up questions:**
        * Explicitly mention what "it" or "that" refers to
        * Connect new information to previous explanations
        * Use consistent terminology with previous answers
    - **Error/debug questions:**
        * Reference similar issues discussed before
        * Build upon previous debugging approaches
        * Maintain consistent solution patterns
    
    2. RESPONSE STRUCTURE:
    - Use clear, natural language
    - Always write code in proper markdown blocks with language specified
    - Example: ```python\nprint("hello")\n```
    - Only include code when specifically asked or necessary
    - Break complex explanations into bullet points
    - When referencing previous topics, use phrases like:
        * "As we discussed earlier about [topic]..."
        * "Building upon our previous discussion of [concept]..."
        * "Connecting this to our earlier example of [example]..."
    """

    # Enhanced domain-specific guidelines
    domain_prompts = {
        'java full stack': """
        3. JAVA FULL STACK GUIDELINES:
        - Clearly separate frontend and backend concepts
        - Use modern ES6+ syntax for JavaScript
        - Reference Spring Boot best practices
        - Maintain context between frontend and backend discussions
        - Connect new concepts to previously explained architecture""",
        
        'data science': """
        3. DATA SCIENCE GUIDELINES:
        - Focus on practical applications
        - Reference pandas/numpy when relevant
        - Explain mathematical concepts simply
        - Build upon previously explained statistical concepts
        - Maintain consistent dataset examples throughout conversation"""
    }

    # Add domain-specific guidelines if they exist
    domain_prompt = domain_prompts.get(domain.lower(), "")
    if domain_prompt:
        base_prompt += domain_prompt
    else:
        base_prompt += f"\n3. {domain.upper()} GUIDELINES:\n- Provide clear explanations relevant to {domain}"

    return base_prompt