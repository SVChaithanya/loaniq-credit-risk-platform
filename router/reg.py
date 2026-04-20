from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from schemas import Register
from auth import generate_customer_id, hash_password
from models import Registration, OTP
from otp_service import generate_otp, hash_otp,get_expiry
from email_service import send_verification_email

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(data: Register, db: Session = Depends(get_db)):

    if db.query(Registration).filter_by(email=data.email).first():
        raise HTTPException(400, "Email already exists")

    customer_id = generate_customer_id(db)

    otp = generate_otp()
    hashed = hash_otp(otp)

    # TRY EMAIL FIRST (IMPORTANT FIX)
    sent = send_verification_email(data.email, data.first_name, otp)

    if not sent:
        raise HTTPException(500, "Email service failed")

    user = Registration(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        customer_id=customer_id,
        password=hash_password(data.password),
        is_verified=False
    )

    db.add(user)
    db.flush()  # get ID before OTP insert

    otp_record = OTP(
        customer_id=customer_id,
        email=data.email,
        otp_hash=hashed,
        purpose="verify",
        expire_at=get_expiry(10)
    )

    db.add(otp_record)
    db.commit()

    return {"message": "OTP sent", "customer_id": customer_id}