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
