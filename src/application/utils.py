import hashlib
import secrets
from fastapi import Request


def get_fingerprint(request: Request) -> str:
    """Return a stable per-client fingerprint for refresh rotation checks."""
    user_agent = request.headers.get('user-agent', '')
    ip = request.client.host if request.client else ''
    return hashlib.sha256(f'{ip}:{user_agent}'.encode()).hexdigest()[:16]


def generate_email_verification_token() -> str:
    return secrets.token_urlsafe(32)


def hash_email_verification_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
