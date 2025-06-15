from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    """Token schema for authentication response."""
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Token payload schema for JWT token."""
    sub: Optional[str] = None
    exp: Optional[int] = None