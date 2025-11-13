from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from typing import List, Optional
from app.models.models import Booking, User
from app.schemas.schemas import BookingCreate, BookingResponse

class BookingService:
    """Service layer for booking operations"""
    
    @staticmethod
    def check_overlap(
        db: Session,
        room_identifier: str,
        start_time: datetime,
        end_time: datetime,
        exclude_booking_id: Optional[int] = None
    ) -> bool:
        """
        Check if a booking overlaps with existing bookings for the same room.
        Returns True if there is an overlap, False otherwise.
        """
        query = db.query(Booking).filter(
            Booking.room_identifier == room_identifier,
            or_(
                # New booking starts during existing booking
                and_(
                    Booking.start_time <= start_time,
                    Booking.end_time > start_time
                ),
                # New booking ends during existing booking
                and_(
                    Booking.start_time < end_time,
                    Booking.end_time >= end_time
                ),
                # New booking completely contains existing booking
                and_(
                    Booking.start_time >= start_time,
                    Booking.end_time <= end_time
                )
            )
        )
        
        if exclude_booking_id:
            query = query.filter(Booking.id != exclude_booking_id)
        
        overlapping_booking = query.first()
        return overlapping_booking is not None
    
    @staticmethod
    def create_booking(db: Session, booking: BookingCreate, user: User) -> Booking:
        """
        Create a new booking after validating no overlaps exist.
        Raises ValueError if there is an overlap.
        """
        # Parse the booking time
        start_time = datetime.strptime(booking.booking_time, '%Y-%m-%d %H:%M')
        end_time = start_time + timedelta(minutes=booking.duration_minutes)
        
        # Check for overlaps
        if BookingService.check_overlap(
            db, 
            booking.room_identifier, 
            start_time, 
            end_time
        ):
            raise ValueError(
                f"Booking overlaps with an existing booking for room {booking.room_identifier}"
            )
        
        # Create the booking
        db_booking = Booking(
            room_identifier=booking.room_identifier,
            user_id=user.id,
            start_time=start_time,
            end_time=end_time
        )
        
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        
        return db_booking
    
    @staticmethod
    def get_bookings_by_room_and_date(
        db: Session,
        room_identifier: str,
        date: str
    ) -> List[Booking]:
        """
        Get all bookings for a specific room on a specific date.
        """
        target_date = datetime.strptime(date, '%Y-%m-%d').date()
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())
        
        bookings = db.query(Booking).filter(
            Booking.room_identifier == room_identifier,
            Booking.start_time >= start_of_day,
            Booking.start_time <= end_of_day
        ).order_by(Booking.start_time).all()
        
        return bookings
    
    @staticmethod
    def get_bookings_by_user_and_date(
        db: Session,
        user_id: int,
        date: str
    ) -> List[Booking]:
        """
        Get all bookings for a specific user on a specific date.
        """
        target_date = datetime.strptime(date, '%Y-%m-%d').date()
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())
        
        bookings = db.query(Booking).filter(
            Booking.user_id == user_id,
            Booking.start_time >= start_of_day,
            Booking.start_time <= end_of_day
        ).order_by(Booking.start_time).all()
        
        return bookings
    
    @staticmethod
    def get_all_bookings_by_date(
        db: Session,
        date: str
    ) -> List[Booking]:
        """
        Get all bookings on a specific date (useful for admin views).
        """
        target_date = datetime.strptime(date, '%Y-%m-%d').date()
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())
        
        bookings = db.query(Booking).filter(
            Booking.start_time >= start_of_day,
            Booking.start_time <= end_of_day
        ).order_by(Booking.room_identifier, Booking.start_time).all()
        
        return bookings
    
    @staticmethod
    def delete_booking(db: Session, booking_id: int, user: User) -> bool:
        """
        Delete a booking. Only the owner can delete their booking.
        Returns True if deleted, raises ValueError if not found or unauthorized.
        """
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        
        if not booking:
            raise ValueError(f"Booking with id {booking_id} not found")
        
        if booking.user_id != user.id:
            raise ValueError("You are not authorized to delete this booking")
        
        db.delete(booking)
        db.commit()
        return True
    
    @staticmethod
    def update_booking(
        db: Session, 
        booking_id: int, 
        booking_update: BookingCreate, 
        user: User
    ) -> Booking:
        """
        Update a booking. Only the owner can update their booking.
        """
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        
        if not booking:
            raise ValueError(f"Booking with id {booking_id} not found")
        
        if booking.user_id != user.id:
            raise ValueError("You are not authorized to update this booking")
        
        # Parse the new booking time
        start_time = datetime.strptime(booking_update.booking_time, '%Y-%m-%d %H:%M')
        end_time = start_time + timedelta(minutes=booking_update.duration_minutes)
        
        # Check for overlaps (excluding the current booking)
        if BookingService.check_overlap(
            db,
            booking_update.room_identifier,
            start_time,
            end_time,
            exclude_booking_id=booking_id
        ):
            raise ValueError(
                f"Updated booking overlaps with an existing booking for room {booking_update.room_identifier}"
            )
        
        # Update the booking
        booking.room_identifier = booking_update.room_identifier
        booking.start_time = start_time
        booking.end_time = end_time
        
        db.commit()
        db.refresh(booking)
        
        return booking