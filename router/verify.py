from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from db import get_db
from schemas import VerifyOTP
from models import Registration, OTP
from otp_service import hash_otp

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/verify")
def verify(data: VerifyOTP, db: Session = Depends(get_db)):

    otp = db.query(OTP).filter(
        OTP.email == data.email,
        OTP.otp_hash == hash_otp(data.otp),
        OTP.purpose == "verify",
        OTP.used == False
    ).first()

    if not otp:
        raise HTTPException(400, "Invalid OTP")

    if otp.expire_at < datetime.now(timezone.utc):
        raise HTTPException(400, "Expired")

    user = db.query(Registration).filter_by(customer_id=otp.customer_id).first()

    user.is_verified = True
    otp.used = True

    db.commit()

    return {"msg": "verified"}