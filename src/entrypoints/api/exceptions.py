from pydantic import BaseModel
from typing import Any, Optional

class ApiError(BaseModel):
    code: str            # machine-readable
    message: str         # human message
    details: Optional[Any] = None  # optional contextual info
