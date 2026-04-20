from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from db import get_db
from auth import get_current_user
from models import FinancialProfile
from schemas import FinancialProfileCreate

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.post("/")
def create_profile(
    data: FinancialProfileCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    existing = db.query(FinancialProfile).filter(FinancialProfile.customer_id == user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists. Use PUT to update.")

    if data.employment_type == "STUDENT":
        years, income, expenses, emis = 0, 0.0, 0.0, 0.0
    else:
        years, income, expenses, emis = (
            data.years_of_experience,
            data.monthly_income,
            data.monthly_expenses,
            data.existing_emis
        )

    profile = FinancialProfile(
        customer_id=user_id,
        employment_type=data.employment_type,
        years_of_experience=years,
        monthly_income=income,
        monthly_expenses=expenses,
        existing_emis=emis
    )
    db.add(profile)
    db.commit()
    return {"status": "created", "message": "Financial profile saved successfully"}


@router.get("/")
def get_profile(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    profile = db.query(FinancialProfile).filter(
        FinancialProfile.customer_id == user_id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return {
        "employment_type":     profile.employment_type,
        "years_of_experience": profile.years_of_experience,
        "monthly_income":      profile.monthly_income,
        "monthly_expenses":    profile.monthly_expenses,
        "existing_emis":       profile.existing_emis,
        "updated_at":          profile.updated_at.isoformat() if profile.updated_at else None
    }


@router.put("/")
def update_profile(
    data: FinancialProfileCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    existing = db.query(FinancialProfile).filter(FinancialProfile.customer_id == user_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Profile not found. Use POST to create first.")

    if data.employment_type == "STUDENT":
        existing.employment_type     = "STUDENT"
        existing.years_of_experience = 0
        existing.monthly_income      = 0.0
        existing.monthly_expenses    = 0.0
        existing.existing_emis       = 0.0
    else:
        existing.employment_type     = data.employment_type
        existing.years_of_experience = data.years_of_experience
        existing.monthly_income      = data.monthly_income
        existing.monthly_expenses    = data.monthly_expenses
        existing.existing_emis       = data.existing_emis

    existing.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"status": "updated", "message": "Financial profile updated successfully"}