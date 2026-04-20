from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from auth import verify_refresh_token, create_access_token, create_refresh_token
from schemas import Refresh

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/refresh")
def refresh(data: Refresh, db: Session = Depends(get_db)):

    token = verify_refresh_token(data.refresh_token, db)

    if not token:
        raise HTTPException(401)

    db.delete(token)
    db.commit()

    return {
        "access": create_access_token(token.customer_id),
        "refresh": create_refresh_token(token.customer_id, db)
    }