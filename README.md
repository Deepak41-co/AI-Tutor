# AI Tutor

AI Tutor is an AI-powered chatbot web application built with Flask and PostgreSQL. It provides an interactive platform for users to chat with an AI tutor, leveraging advanced language models via the GROQ API.

## Features
- Interactive AI chatbot for tutoring and Q&A
- User-friendly web interface
- Persistent chat history stored in PostgreSQL
- Environment-based configuration
- Easy to set up and run locally

## Prerequisites
- Python 3.8 or higher
- PostgreSQL (running locally or accessible remotely)
- [pip](https://pip.pypa.io/en/stable/)

## Setup Instructions

### 1. Clone the Repository
```sh
git clone https://github.com/yourusername/AI-Tutor-main.git
cd AI-Tutor-main
```

### 2. Create and Activate a Virtual Environment (Recommended)
```sh
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Configure Environment Variables
- Copy the provided `env.example` to `.env`:
  ```sh
  copy env.example .env  # On Windows
  # or
  cp env.example .env    # On macOS/Linux
  ```
- Edit `.env` and fill in your actual credentials and API keys.

### 5. Set Up the Database
- Ensure PostgreSQL is running and a database is created (default: `AI_chatbot`).
- Update `DATABASE_URL` in `.env` if needed.
- Run migrations:
  ```sh
  flask db upgrade
  ```

### 6. Run the Application
You can start the server with:
```sh
python app.py
```

Or, if you prefer using Flask CLI:
```sh
flask run
```

Both commands will launch the API at [http://127.0.0.1:5000](http://127.0.0.1:5000).



## API Endpoints

This project exposes a robust REST API for AI-powered tutoring, session management, chat history, and feedback. Below are the main endpoints:

### 1. Start a Session
- **POST** `/api/start-session`
- **Body:**
  ```json
  {
    "name": "Your Name",
    "email": "your@email.com",
    "domain": "math"
  }
  ```
- **Response:** Student info and welcome message.

### 2. Chat with the AI Tutor
- **POST** `/api/chat`
- **Body:**
  ```json
  {
    "student_id": 1,
    "query": "What is the Pythagorean theorem?",
    "session_id": "session_1_1717000000" // Optional
  }
  ```
- **Response:** AI-generated answer, chat/session IDs.

### 3. Get Student Sessions
- **GET** `/api/student/sessions/<student_id>`
- **Response:** List of all chat sessions for the student, with first message, timestamps, and message count.

### 4. Get Chat History
- **GET** `/api/chat-history/<student_id>?session_id=<session_id>`
- **Response:** Chronological list of all messages (user and bot) for a session.

### 5. Submit Feedback
- **POST** `/api/feedback`
- **Body:**
  ```json
  {
    "chat_id": 123,
    "helpful": true
  }
  ```
- **Response:** Feedback confirmation.

---

## Why AI Tutor Has Great Potential

- **Modern Tech Stack:** Built with Flask, SQLAlchemy, PostgreSQL, and GROQ LLMs for scalable, production-ready AI tutoring.
- **Session & Context Management:** Remembers user sessions, domains, and chat history for personalized, context-aware tutoring.
- **Extensible:** Easily add new endpoints, domains, or AI models. The codebase is modular and ready for growth.
- **Feedback Loop:** Built-in feedback endpoint for continuous improvement and analytics.
- **Secure & Configurable:** Uses environment variables for all secrets and configuration.
- **Open Source:** MIT License—fork, extend, and deploy for your own use case!

## Example Use Cases
- Personalized tutoring for students in any subject
- Internal company knowledge bots
- EdTech platforms seeking AI-powered chat
- Research on conversational AI and education

## Frontend Integration

This project is a **backend and AI engine only** solution. It exposes a powerful REST API for use with any frontend or client. You can connect it to:
- Custom web frontends (React, Vue, Angular, etc.)
- Mobile apps (iOS, Android, Flutter, etc.)
- No-code tools (Retool, Bubble, etc.)
- Chatbot widgets or other platforms

**No frontend is included in this repository.**

You can quickly test and integrate the API using Postman, cURL, or by building your own UI.

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the MIT License.
