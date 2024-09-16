from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    instrument: str

# Which fields are sent back to the client
class UserOut(BaseModel):
    username: str
    instrument: str
    is_admin: bool

    class Config:
        # Tells Pydantic to read the data not from simple dictionaries but from ORM objects (like SQLAlchemy models), allowing Pydantic to work directly with database models.
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    is_admin: bool
    instrument: str

# Validates JWT - Ensures that the token contains a valid username when parsing the token data
class TokenData(BaseModel):
    username: str | None = None