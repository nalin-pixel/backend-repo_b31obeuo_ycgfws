import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import User, Hotel, Booking, ContactMessage

app = FastAPI(title="Hotel Booking API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility to convert Mongo docs

def serialize_doc(doc):
    d = dict(doc)
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    return d

@app.get("/")
def root():
    return {"message": "Hotel Booking Backend is running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response

# Auth (simple demo)
class LoginPayload(BaseModel):
    email: str
    password: str

@app.post("/api/auth/register")
def register_user(user: User):
    # Check if email exists
    existing = db["user"].find_one({"email": user.email}) if db else None
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_id = create_document("user", user)
    return {"id": user_id, "name": user.name, "email": user.email}

@app.post("/api/auth/login")
def login(payload: LoginPayload):
    doc = db["user"].find_one({"email": payload.email}) if db else None
    if not doc or doc.get("password") != payload.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"token": str(doc.get("_id")), "name": doc.get("name"), "email": doc.get("email")}

# Hotels
@app.get("/api/hotels", response_model=List[dict])
def list_hotels():
    hotels = get_documents("hotel") if db else []
    return [serialize_doc(h) for h in hotels]

@app.post("/api/hotels")
def create_hotel(hotel: Hotel):
    hotel_id = create_document("hotel", hotel)
    return {"id": hotel_id}

# Booking
@app.post("/api/bookings")
def create_booking(booking: Booking):
    # Validate referenced docs exist
    if not ObjectId.is_valid(booking.user_id) or not ObjectId.is_valid(booking.hotel_id):
        raise HTTPException(status_code=400, detail="Invalid IDs")
    if not db["user"].find_one({"_id": ObjectId(booking.user_id)}):
        raise HTTPException(status_code=404, detail="User not found")
    if not db["hotel"].find_one({"_id": ObjectId(booking.hotel_id)}):
        raise HTTPException(status_code=404, detail="Hotel not found")
    booking_id = create_document("booking", booking)
    return {"id": booking_id}

# Contact messages
@app.post("/api/contact")
def contact(msg: ContactMessage):
    msg_id = create_document("contactmessage", msg)
    return {"id": msg_id, "status": "received"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
