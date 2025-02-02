import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionManager:
    """
    A class to manage user sessions with tiemout and conversation history.
    """
    def __init__(self, session_timeout_minutes: int = 30):
        """
        Initialize the SessionManager with a session timeout.

        :param session_timeout_minutes: Timeout duration for sessions in  minutes.
        """
        self.sessions: Dict[str, dict] = {}
        self.timeout = timedelta(minutes=session_timeout_minutes)

    def create_session(self) -> str:
        """
        Create a new session and return its ID.

        :return: The session ID.
        """
        try:
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = {
                'created_at': datetime.now(),
                'last_accessed': datetime.now(),
                'conversation_history': []
            }
            return session_id
        except:
            logger.error(f"Error creating session: {str(e)}")

    def get_session(self, session_id: str) -> Optional[dict]:
        """
        Retreive a session by its ID.

        :param session_id: The session ID.
        :return: The session data or None if the session is expired or not found.
        """
        try:
            session = self.sessions.get(session_id)
            if session:
                if datetime.now() - session['last_accessed'] > self.timeout:
                    self.sessions.pop(session_id)
                    return None
                session['last_accessed'] = datetime.now()
            return session
        except Exception as e:
            logger.error(f"Error retrieving session: {str(e)}")

    def update_conversation(self, session_id: str, question: str, answer: str):
        """
        Update the conversation history of a session.

        :param session_id: The session ID.
        :param question: The question asked.
        :param answer: The answer provided.
        """
        try:
            if session := self.get_session(session_id):
                session['conversation_history'].append({
                    'question': question,
                    'answer': answer,
                    'timestamp': datetime.now()
                })

                session['conversation_history'] = session['conversation_history'][-5:]
        except Exception as e:
            logger.error(f"Error updating conversation: {str(e)}")
