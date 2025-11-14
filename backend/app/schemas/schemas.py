from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    
    user_identifier: str = Field(
        ..., 
        min_length=3, 
        max_length=50,
        description="Unique username identifier",
        examples=["john.doe"]
    )
    password: str = Field(
        ..., 
        min_length=6,
        description="User password (will be hashed)",
        examples=["securepassword123"]
    )

class UserLogin(BaseModel):
    
    user_identifier: str = Field(..., description="Username identifier")
    password: str = Field(..., description="User password")

class UserResponse(BaseModel):
    
    id: int
    user_identifier: str
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    
    user_identifier: Optional[str] = None
    user_id: Optional[int] = None

class BookingCreate(BaseModel):
    
    room_identifier: str = Field(
        ..., 
        description="Room identifier in MACRO_CASE",
        examples=["EVEREST", "KINABALU", "RINJANI"]
    )
    booking_time: str = Field(
        ..., 
        description="Booking start time in 'YYYY-MM-DD HH:MM' format",
        examples=["2025-11-15 14:30"]
    )
    duration_minutes: int = Field(
        default=60, 
        ge=10,
        description="Duration in minutes (must be multiple of 10)",
        examples=[60, 90, 120]
    )
    
    @field_validator('room_identifier')
    def validate_room_identifier(cls, v):
        if not v.isupper():
            raise ValueError('room_identifier must be in MACRO_CASE (all uppercase)')
        if not v.replace('_', '').isalnum():
            raise ValueError('room_identifier must contain only letters, numbers, and underscores')
        return v
    
    @field_validator('booking_time')
    def validate_booking_time(cls, v):
        try:
            dt = datetime.strptime(v, '%Y-%m-%d %H:%M')
            if dt.minute % 10 != 0:
                raise ValueError('Minutes must be in 10-minute increments (00, 10, 20, 30, 40, 50)')
        except ValueError as e:
            if 'does not match format' in str(e):
                raise ValueError('booking_time must be in YYYY-MM-DD HH:MM format')
            raise
        return v
    
    @field_validator('duration_minutes')
    def validate_duration(cls, v):
        if v % 10 != 0:
            raise ValueError('duration_minutes must be a multiple of 10')
        return v

class BookingResponse(BaseModel):
   
    id: int
    room_identifier: str
    user_id: int
    user_identifier: str
    start_time: datetime
    end_time: datetime
    
    @model_validator(mode='before')
    @classmethod
    def extract_user_identifier(cls, data):
        """Extract user_identifier from the related User object"""
        if isinstance(data, dict):
            return data
        
        # If it's a SQLAlchemy model (Booking object)
        if hasattr(data, 'user') and hasattr(data.user, 'user_identifier'):
            # Convert to dict and add user_identifier
            result = {
                'id': data.id,
                'room_identifier': data.room_identifier,
                'user_id': data.user_id,
                'user_identifier': data.user.user_identifier,
                'start_time': data.start_time,
                'end_time': data.end_time,
            }
            return result
        
        return data
    
    @property
    def booking_time(self) -> str:
        return self.start_time.strftime('%Y-%m-%d %H:%M')
    
    @property
    def duration_minutes(self) -> int:
        return int((self.end_time - self.start_time).total_seconds() / 60)
    
    model_config = ConfigDict(from_attributes=True)

class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str