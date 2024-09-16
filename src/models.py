from sqlalchemy import Column, Integer, String, Boolean, Text
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    instrument = Column(String)
    is_admin = Column(Boolean, default=False)


# Songs to PostgreSQL
class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    song_name = Column(String, index=True, unique=True, nullable=False)
    author = Column(String, nullable=False)
    lyrics = Column(Text, nullable=False)