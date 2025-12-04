import enum
import uuid
from dataclasses import dataclass
from datetime import datetime


class TokenType(enum.Enum):
    ACCESS = 'access'
    REFRESH = 'refresh'


@dataclass(frozen=True)
class TokenPayload:
    subject: uuid.UUID
    jti: uuid.UUID
    issued_at: datetime
    expires_at: datetime
    token_type: TokenType


@dataclass
class RefreshToken:
    id: uuid.UUID
    user_id: uuid.UUID
    jti: uuid.UUID
    fingerprint: str
    created_at: datetime
    expires_at: datetime
    is_revoked: bool = False

    def revoke(self, now: datetime) -> None:
        self.is_revoked = True
