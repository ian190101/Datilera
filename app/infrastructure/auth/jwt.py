
from datetime import datetime, timedelta, timezone
from jwt import encode, decode, PyJWTError
from pydantic import BaseModel

from app.config.settings import Settings

class TokenData(BaseModel):
    sub: str  # Subject (username)
    id: int   # User ID
    # Add other claims as needed

def create_access_token(data: dict, settings: Settings) -> str:

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_exp_minutes)

    to_encode.update({"exp": expire})

    encoded_jwt = encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    return encoded_jwt



def create_refresh_token(data: dict, settings: Settings) -> str:

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)

    to_encode.update({"exp": expire})

    encoded_jwt = encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    return encoded_jwt



def decode_token(token: str, settings: Settings) -> TokenData | None:

    try:

        payload = decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])

        return TokenData(**payload)

    except PyJWTError:

        return None
