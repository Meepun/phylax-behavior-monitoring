# storage for user session states

from models.session import SessionState

_sessions = {}

def get_session(user_id):
    if user_id not in _sessions:
        _sessions[user_id] = SessionState(user_id)
    return _sessions[user_id]
