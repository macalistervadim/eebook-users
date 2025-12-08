import hashlib

from fastapi import Request


def get_fingerprint(request: Request) -> str:
    ip = request.client.host if request.client else 'unknown'
    ua = request.headers.get('user-agent', '')
    return f'{ip}:{hashlib.sha256(ua.encode()).hexdigest()[:16]}'
