"""Wiring used by the web layer."""
from auth.sessions import SessionStore

sessions = SessionStore()


def login(user_id: str) -> str:
    return sessions.create(user_id)


def current_user(token: str) -> str | None:
    return sessions.touch(token)
