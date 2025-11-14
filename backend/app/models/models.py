from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.db import Base

class User(Base):
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_identifier = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Relationship to bookings
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, user_identifier='{self.user_identifier}')>"


class Booking(Base):
   
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    room_identifier = Column(String, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    
    # Relationship to user
    user = relationship("User", back_populates="bookings")
    
    def __repr__(self):
        return (
            f"<Booking(id={self.id}, room='{self.room_identifier}', "
            f"user_id={self.user_id}, start={self.start_time})>"
        )