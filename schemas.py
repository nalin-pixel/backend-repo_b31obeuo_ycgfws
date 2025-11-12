"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user"
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=4, description="Plain password for demo only")

class Hotel(BaseModel):
    """Hotels collection schema: 5-star hotels"""
    name: str
    city: str
    country: str
    price_per_night: float = Field(..., ge=0)
    rating: float = Field(..., ge=0, le=5)
    image: Optional[str] = None
    description: Optional[str] = None
    amenities: List[str] = []
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class Booking(BaseModel):
    """Bookings collection schema"""
    user_id: str
    hotel_id: str
    check_in: str  # ISO date string
    check_out: str  # ISO date string
    guests: int = Field(..., ge=1)
    phone: Optional[str] = None
    special_requests: Optional[str] = None

class ContactMessage(BaseModel):
    """Contact messages from users"""
    name: str
    email: EmailStr
    phone: Optional[str] = None
    message: str
