import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional

class SessionManager:
    def __init__(self, session_timeout_minutes: int = 30):
        self.sessions: Dict[str, dict] = {}
        self.timeout = timedelta(minutes=session_timeout_minutes)

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'created_at': datetime.now(),
            'last_accessed': datetime.now(),
            'conversation_history': []
        }
        return session_id

    def get_session(self, session_id: str) -> Optional[dict]:
        session = self.sessions.get(session_id)
        if session:
            if datetime.now() - session['last_accessed'] > self.timeout:
                self.sessions.pop(session_id)
                return None
            session['last_accessed'] = datetime.now()
        return session

    def update_conversation(self, session_id: str, question: str, answer: str):
        if session := self.get_session(session_id):
            session['conversation_history'].append({
                'question': question,
                'answer': answer,
                'timestamp': datetime.now()
            })

            session['conversation_history'] = session['conversation_history'][-5:]
