"""In-memory login sessions with idle and absolute expiry."""
import secrets
import time
from dataclasses import dataclass

IDLE_TIMEOUT_SECONDS = 30 * 60
ABSOLUTE_TIMEOUT_SECONDS = 12 * 60 * 60


@dataclass
class _Session:
    user_id: str
    created_at: float
    last_seen: float


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, _Session] = {}

    def create(self, user_id: str) -> str:
        now = time.time()
        token = secrets.token_urlsafe(32)
        self._sessions[token] = _Session(user_id, created_at=now, last_seen=now)
        return token

    def touch(self, token: str) -> str | None:
        """Returns the user id for a live session and refreshes its idle timer, or None."""
        session = self._sessions.get(token)
        if session is None:
            return None
        now = time.time()
        if now - session.last_seen > IDLE_TIMEOUT_SECONDS or now - session.created_at > ABSOLUTE_TIMEOUT_SECONDS:
            del self._sessions[token]
            return None
        session.last_seen = now
        return session.user_id

    def revoke(self, token: str) -> None:
        self._sessions.pop(token, None)

    def revoke_user(self, user_id: str) -> int:
        tokens = [t for t, s in self._sessions.items() if s.user_id == user_id]
        for t in tokens:
            del self._sessions[t]
        return len(tokens)
