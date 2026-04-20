from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import Login
from db import get_db
from models import Registration
from auth import verify_password, create_access_token, create_refresh_token, OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
def login(data: Login, db: Session = Depends(get_db)):

    user = db.query(Registration).filter_by(customer_id=data.customer_id).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(401)

    if not user.is_verified:
        raise HTTPException(403, "Not verified")

    return {
        "access": create_access_token(user.customer_id),
        "refresh": create_refresh_token(user.customer_id, db)
    }