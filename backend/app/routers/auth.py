from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database.db import get_db
from app.schemas.schemas import UserCreate, UserLogin, UserResponse, Token, ErrorResponse
from app.services.auth_service import AuthService, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from app.models.models import User

router = APIRouter(
    prefix="/api/auth",
    tags=["authentication"]
)

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "User registered successfully"},
        400: {"model": ErrorResponse, "description": "User already exists"}
    },
    summary="Register a new user",
    description="Create a new user account with username and password"
)
def register(user: UserCreate, db: Session = Depends(get_db)):

    try:
        db_user = AuthService.create_user(
            db, 
            user_identifier=user.user_identifier,
            password=user.password
        )
        return db_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/login",
    response_model=Token,
    responses={
        200: {"description": "Login successful"},
        401: {"model": ErrorResponse, "description": "Invalid credentials"}
    },
    summary="Login",
    description="Authenticate and receive a JWT access token"
)
def login(user: UserLogin, db: Session = Depends(get_db)):
    
    authenticated_user = AuthService.authenticate_user(
        db,
        user_identifier=user.user_identifier,
        password=user.password
    )
    
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={
            "sub": authenticated_user.user_identifier,
            "user_id": authenticated_user.id
        },
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the currently authenticated user's information"
)
def get_me(current_user: User = Depends(get_current_user)):
    """Get information about the currently authenticated user"""
    return current_user