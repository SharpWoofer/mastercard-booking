from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.db import get_db
from app.schemas.schemas import BookingCreate, BookingResponse, ErrorResponse
from app.services.booking_service import BookingService
from app.services.auth_service import get_current_user
from app.models.models import User

router = APIRouter(
    prefix="/api/bookings",
    tags=["bookings"]
)

@router.post(
    "/",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Booking created successfully"},
        400: {"model": ErrorResponse, "description": "Invalid input or booking overlap"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        422: {"description": "Validation error"}
    },
    summary="Create a new booking",
    description="Creates a new room booking. Requires authentication. Rejects the request if the timing overlaps with an existing booking for the same room."
)
def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new booking with the following requirements:
    - **room_identifier**: Room name in MACRO_CASE (e.g., EVEREST, KINABALU, RINJANI)
    - **booking_time**: Start time in 'YYYY-MM-DD HH:MM' format, minutes must be in 10-minute increments
    - **duration_minutes**: Duration in minutes (must be multiple of 10, default is 60)
    
    **Authentication required**: Include JWT token in Authorization header as "Bearer {token}"
    
    Returns the created booking or an error if there's an overlap.
    """
    try:
        db_booking = BookingService.create_booking(db, booking, current_user)
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        # Manually set user_identifier for response
        response = BookingResponse.model_validate(db_booking)
        response.user_identifier = current_user.user_identifier
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the booking: {str(e)}"
        )

@router.get(
    "/",
    response_model=List[BookingResponse],
    responses={
        200: {"description": "List of bookings retrieved successfully"},
        400: {"model": ErrorResponse, "description": "Invalid query parameters"},
        422: {"description": "Validation error"}
    },
    summary="Get bookings by room or user and date",
    description="Retrieves all bookings for a specific room OR the current user on a given date."
)
def get_bookings(
    date: str = Query(
        ..., 
        description="Date in YYYY-MM-DD format",
        example="2025-11-15"
    ),
    room_identifier: Optional[str] = Query(
        None,
        description="Room identifier in MACRO_CASE format",
        example="EVEREST"
    ),
    my_bookings: bool = Query(
        False,
        description="If true, returns only your bookings for the date"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get bookings filtered by:
    - **date**: Required. Date in YYYY-MM-DD format
    - **room_identifier**: Optional. Filter by room (MACRO_CASE)
    - **my_bookings**: Optional. If true, returns only your bookings
    
    **Authentication required**: Include JWT token in Authorization header
    
    Returns a list of bookings sorted by start time.
    """
    try:
        if my_bookings:
            bookings = BookingService.get_bookings_by_user_and_date(
                db, current_user.id, date
            )
            if room_identifier:
                bookings = [b for b in bookings if b.room_identifier == room_identifier]
        elif room_identifier:
            bookings = BookingService.get_bookings_by_room_and_date(
                db, room_identifier, date
            )
        else:
            bookings = BookingService.get_all_bookings_by_date(db, date)
        
        # Add user_identifier to each booking
        responses = []
        for booking in bookings:
            response = BookingResponse.model_validate(booking)
            response.user_identifier = booking.user.user_identifier
            responses.append(response)
        
        return responses
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving bookings: {str(e)}"
        )

@router.put(
    "/{booking_id}",
    response_model=BookingResponse,
    responses={
        200: {"description": "Booking updated successfully"},
        400: {"model": ErrorResponse, "description": "Invalid input or booking overlap"},
        401: {"model": ErrorResponse, "description": "Not authenticated or not authorized"},
        404: {"model": ErrorResponse, "description": "Booking not found"}
    },
    summary="Update a booking",
    description="Update an existing booking. Only the booking owner can update it."
)
def update_booking(
    booking_id: int,
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing booking:
    - **booking_id**: ID of the booking to update
    - **room_identifier**: New room name in MACRO_CASE
    - **booking_time**: New start time in 'YYYY-MM-DD HH:MM' format
    - **duration_minutes**: New duration in minutes
    
    **Authorization**: Only the booking owner can update their booking
    """
    try:
        db_booking = BookingService.update_booking(db, booking_id, booking, current_user)
        response = BookingResponse.model_validate(db_booking)
        response.user_identifier = current_user.user_identifier
        return response
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while updating the booking: {str(e)}"
        )

@router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Booking deleted successfully"},
        401: {"model": ErrorResponse, "description": "Not authenticated or not authorized"},
        404: {"model": ErrorResponse, "description": "Booking not found"}
    },
    summary="Delete a booking",
    description="Delete an existing booking. Only the booking owner can delete it."
)
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an existing booking:
    - **booking_id**: ID of the booking to delete
    
    **Authorization**: Only the booking owner can delete their booking
    """
    try:
        BookingService.delete_booking(db, booking_id, current_user)
        return None
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while deleting the booking: {str(e)}"
        )