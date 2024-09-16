from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    instrument: str

class UserOut(BaseModel):
    username: str
    instrument: str
    is_admin: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    is_admin: bool
    instrument: str

# Validates JWT - Ensures that the token contains a valid username when parsing the token data
class TokenData(BaseModel):
    username: str | None = None