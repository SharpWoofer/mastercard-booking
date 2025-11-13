# 📚 Meeting Room Booking System API

A modern REST API for meeting room booking built with FastAPI and PostgreSQL. This system allows users to book meeting rooms, view existing bookings, and manage their reservations through a clean RESTful interface.

[Python](https://img.shields.io/badge/Python-3.14-blue)
[FastAPI](https://img.shields.io/badge/FastAPI-0.115.5-green)
[PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791)
[Docker](https://img.shields.io/badge/Docker-Compose-2496ED)

---

## 🌟 Features

- **🔐 JWT Authentication**: Secure token-based authentication system
- **📅 Room Booking**: Create bookings with date/time selection
- **👀 View Bookings**: Query bookings by date, room, or user
- **✏️ Manage Bookings**: Update or delete your own bookings
- **⏰ Time Validation**: Automatic validation for 10-minute time increments
- **🚫 Conflict Prevention**: Prevents double-booking of rooms
- **📖 Interactive API Docs**: Swagger UI and ReDoc documentation
- **🧪 Comprehensive Tests**: Full test coverage with pytest

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Application                     │
│  - JWT Authentication (auth.py)                         │
│  - Booking Management (bookings.py)                     │
│  - Pydantic Validation (schemas.py)                     │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                SQLAlchemy ORM Layer                      │
│  - User Model                                            │
│  - Booking Model                                         │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                PostgreSQL Database                       │
│  - User authentication & management                      │
│  - Booking records & relationships                       │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Prerequisites

Before you begin, ensure you have **Docker Desktop** installed

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/SharpWoofer/mastercard-booking.git
cd mastercard-booking
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```env
DB_USER=myuser
DB_PASSWORD=mypassword
DB_HOST=db
DB_PORT=5432
DB_NAME=mydatabase
SECRET_KEY=
```

### 3. Build and Run with Docker

```bash
# Start all services (API and database)
docker compose up --build

# Check if containers are running
docker-compose ps
```

You should see three containers running:
- `mastercard-booking-adminer-1`
- `mastercard-booking-backend`
- `mastercard-booking-db-1  `

### 4. Access the Application

- **API Base URL**: http://localhost:8050
- **Interactive API Documentation (Swagger)**: http://localhost:8050/docs
- **Alternative API Documentation (ReDoc)**: http://localhost:8050/redoc

---

## 📖 Example Usage

### Step 1: Register a New User

**Endpoint**: `POST /api/auth/register`

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "user_identifier": "john.doe",
    "password": "securepassword123"
  }'
```

**Response**:
```json
{
  "id": 1,
  "user_identifier": "john.doe"
}
```

### Step 2: Login and Get Access Token

**Endpoint**: `POST /api/auth/login`

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john.doe&password=securepassword123"
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Step 3: Create a Booking

**Endpoint**: `POST /api/bookings/`

```bash
curl -X POST "http://localhost:8000/api/bookings/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "room_identifier": "EVEREST",
    "booking_time": "2025-11-20 14:00",
    "duration_minutes": 60
  }'
```

**Response**:
```json
{
  "id": 1,
  "room_identifier": "EVEREST",
  "user_id": 1,
  "user_identifier": "john.doe",
  "booking_time": "2025-11-20 14:00",
  "end_time": "2025-11-20 15:00"
}
```

### Step 4: View All Bookings

**Endpoint**: `GET /api/bookings/`

```bash
curl -X GET "http://localhost:8000/api/bookings/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Filter by date**:
```bash
curl -X GET "http://localhost:8000/api/bookings/?date=2025-11-20" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Filter by room**:
```bash
curl -X GET "http://localhost:8000/api/bookings/?room_identifier=EVEREST" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**View your own bookings**:
```bash
curl -X GET "http://localhost:8000/api/bookings/?user=me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Step 5: Update a Booking

**Endpoint**: `PUT /api/bookings/{booking_id}`

```bash
curl -X PUT "http://localhost:8000/api/bookings/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "room_identifier": "K2",
    "booking_time": "2025-11-20 15:00",
    "duration_minutes": 90
  }'
```

### Step 6: Delete a Booking

**Endpoint**: `DELETE /api/bookings/{booking_id}`

```bash
curl -X DELETE "http://localhost:8000/api/bookings/1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response**:
```json
{
  "message": "Booking deleted successfully"
}
```

---

## 🧪 Running Tests

The project includes comprehensive tests for all endpoints and functionality.

### Run All Tests

```bash
# Run all tests with verbose output
docker-compose exec api pytest -v

# Run with coverage report
docker-compose exec api pytest --cov=app --cov-report=term-missing

# Run with HTML coverage report
docker-compose exec api pytest --cov=app --cov-report=html
# View report at htmlcov/index.html
```

### Run Specific Test Files

```bash
# Test authentication only
docker-compose exec api pytest app/tests/test_auth.py -v

# Test bookings only
docker-compose exec api pytest app/tests/test_bookings.py -v
```

### Expected Test Output

```
======================== test session starts =========================
platform linux -- Python 3.14.0, pytest-9.0.1, pluggy-1.5.0
collected 18 items

app/tests/test_auth.py::test_register_user PASSED              [  5%]
app/tests/test_auth.py::test_register_duplicate_user PASSED    [ 11%]
app/tests/test_auth.py::test_login_success PASSED              [ 16%]
app/tests/test_auth.py::test_login_invalid_credentials PASSED  [ 22%]
app/tests/test_bookings.py::test_create_booking PASSED         [ 27%]
app/tests/test_bookings.py::test_create_booking_invalid_time PASSED [ 33%]
app/tests/test_bookings.py::test_create_booking_conflict PASSED [ 38%]
app/tests/test_bookings.py::test_get_bookings PASSED           [ 44%]
app/tests/test_bookings.py::test_get_bookings_by_date PASSED   [ 50%]
app/tests/test_bookings.py::test_get_bookings_by_room PASSED   [ 55%]
app/tests/test_bookings.py::test_get_my_bookings PASSED        [ 61%]
app/tests/test_bookings.py::test_update_booking PASSED         [ 66%]
app/tests/test_bookings.py::test_update_other_user_booking PASSED [ 72%]
app/tests/test_bookings.py::test_delete_booking PASSED         [ 77%]
app/tests/test_bookings.py::test_delete_other_user_booking PASSED [ 83%]
app/tests/test_bookings.py::test_unauthorized_access PASSED    [ 88%]
app/tests/test_bookings.py::test_invalid_room PASSED           [ 94%]
app/tests/test_bookings.py::test_invalid_duration PASSED       [100%]

======================== 18 passed in 4.23s =========================
```

---

## 📁 Project Structure

```
meeting-room-booking/
├── app/
│   ├── main.py
│   ├── database/
│   │   └── db.py
│   ├── models/
│   │   └── models.py
│   ├── routers/
│   │   ├── auth.py
│   │   └── bookings.py
│   ├── schemas/
│   │   └── schemas.py
│   ├── services/
│   │   └── auth_service.py
│   └── tests/
│       ├── conftest.py
│       ├── test_auth.py
│       └── test_bookings.py
├── .env
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## 🔧 API Endpoints Reference

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login and get token | No |

### Bookings

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/bookings/` | Create new booking | Yes |
| GET | `/api/bookings/` | Get all bookings (with filters) | Yes |
| GET | `/api/bookings/{id}` | Get specific booking | Yes |
| PUT | `/api/bookings/{id}` | Update booking | Yes (owner only) |
| DELETE | `/api/bookings/{id}` | Delete booking | Yes (owner only) |

### Query Parameters for GET `/api/bookings/`

- `date` (optional): Filter by date (format: YYYY-MM-DD)
- `room_identifier` (optional): Filter by room (EVEREST, K2, or KINABALU)
- `user` (optional): Use "me" to get only your bookings

---

## 🔒 Security Features

- **Password Hashing**
- **JWT Tokens**
- **Token Validation**
- **Authorization**
- **SQL Injection Prevention**
- **Input Validation**
---

## 📝 License

This project is licensed under the MIT License.
