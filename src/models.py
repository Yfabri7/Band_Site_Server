from sqlalchemy import Column, Integer, String, Boolean, Text
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)  # Add length here
    hashed_password = Column(String(255))  # Add length here
    instrument = Column(String(50))  # Add length here
    is_admin = Column(Boolean, default=False)


# Songs to PostgreSQL
class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    song_name = Column(String(100), index=True, nullable=False)  # Add length here
    author = Column(String(100), nullable=False)  # Add length here
    lyrics = Column(Text, nullable=False)