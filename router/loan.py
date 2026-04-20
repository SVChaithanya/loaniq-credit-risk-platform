from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
import joblib
import logging
from datetime import datetime, timezone

from auth import get_current_user
from db import get_db
from schemas import LoanRequest
from models import Risk, FinancialProfile

router = APIRouter(prefix="/loan", tags=["Loan"])
logger = logging.getLogger(__name__)

# ─────────────────────────────────
# LOAD MODEL
# ─────────────────────────────────
model = joblib.load("model.pkl")
features = joblib.load("features.pkl")

# ─────────────────────────────────
# CONFIG
# ─────────────────────────────────
LGD = 0.45
MIN_INCOME = 1000

# ─────────────────────────────────
# BANK DATA
# ─────────────────────────────────
BANK_INTEREST = {
    "sbi": 8.5, "hdfc": 9.0, "icici": 9.5,
    "axis": 9.25, "kotak": 9.0, "idfc": 9.75,
    "federal": 9.5, "indian_bank": 8.75,
    "bank_of_baroda": 8.6, "indusind": 9.8,
    "union_bank": 8.7, "canara": 8.65,
    "pnb": 8.75, "rbl": 10.5, "yes_bank": 10.0,
    "boi": 8.8, "others": 10.0,
}

ALT_BANKS = ["sbi", "hdfc", "icici"]

# ─────────────────────────────────
# HELPERS
# ─────────────────────────────────

def normalize_key(key: str) -> str:
    return key.lower().replace(" ", "_")

def calculate_emi(p, rate, months):
    r = rate / (12 * 100)
    if r == 0:
        return p / months
    return p * r * (1 + r) ** months / ((1 + r) ** months - 1)

def calculate_interest_rate(bank, pd_score):
    base = BANK_INTEREST.get(bank, 10.0)
    return round(base + (pd_score * 5), 2)

def get_grade(pd):
    if pd < 0.10: return "A"
    elif pd < 0.20: return "B"
    elif pd < 0.30: return "C"
    elif pd < 0.40: return "D"
    elif pd < 0.50: return "E"
    return "F"

def generate_feedback(pd, dti, emi, income):
    insights, suggestions = [], []

    if pd < 0.2:
        insights.append("Low default risk")
    elif pd < 0.4:
        insights.append("Moderate risk")
    else:
        insights.append("High risk")

    if dti < 40:
        insights.append("Debt level manageable")
    else:
        insights.append("High debt burden")

    if dti > 40:
        suggestions.append("Reduce existing EMIs")

    if emi > income * 0.4:
        suggestions.append("Increase tenure to lower EMI")

    if pd > 0.3:
        suggestions.append("Reduce loan amount")

    if not suggestions:
        suggestions.append("Profile looks strong")

    return insights, suggestions

def get_alternatives(amount, pd):
    results = []
    for b in ALT_BANKS:
        rate = calculate_interest_rate(b, pd)
        emi = calculate_emi(amount, rate, 36)
        results.append({
            "bank": b.upper(),
            "interest_rate": round(rate, 2),
            "emi": round(emi, 2),
        })
    return results

# ─────────────────────────────────
# MAIN API
# ─────────────────────────────────

@router.post("/")
def loan_assessment(
    data: LoanRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    profile = db.query(FinancialProfile).filter(
        FinancialProfile.customer_id == user_id
    ).first()

    if not profile:
        raise HTTPException(404, "Profile not found")

    # ── Basic values ──
    bank = normalize_key(data.bank_name)
    monthly_income = max(profile.monthly_income or MIN_INCOME, MIN_INCOME)
    annual_inc = monthly_income * 12
    existing_emis = profile.existing_emis or 0
    months = 36 if data.term == "36 months" else 60

    # ── Model input ──
    base_dti = (existing_emis / monthly_income) * 100

    input_df = pd.DataFrame([{
        "loan_amnt": data.loan_amnt,
        "annual_inc": annual_inc,
        "dti": round(base_dti, 2),
        "fico_mean": 700,
        "int_rate": BANK_INTEREST.get(bank, 10),
        "term": data.term,
        "grade": "B",
        "purpose": data.purpose,
    }])

    try:
        input_df = input_df[features]
        base_pd = float(model.predict_proba(input_df)[0][1])
    except Exception as e:
        logger.error(f"Model error: {e}")
        base_pd = 0.2

    # ── Financial calculations ──
    interest_rate = calculate_interest_rate(bank, base_pd)
    emi = calculate_emi(data.loan_amnt, interest_rate, months)

    dti = ((existing_emis + emi) / monthly_income) * 100
    foir = dti  # same formula in your case
    lti = data.loan_amnt / annual_inc
    expected_loss = base_pd * LGD * data.loan_amnt
    fico = 700

    # ── Decision ──
    if base_pd < 0.25 and dti < 40:
        decision = "accept"
    elif base_pd < 0.45:
        decision = "review"
    else:
        decision = "reject"

    # ── Feedback ──
    insights, suggestions = generate_feedback(base_pd, dti, emi, monthly_income)
    alternatives = get_alternatives(data.loan_amnt, base_pd)

    # ── Save ──
    record = Risk(
        customer_id=user_id,
        bank_name=data.bank_name,
        loan_amnt=data.loan_amnt,
        annual_inc=annual_inc,
        base_pd=base_pd,
        adjusted_pd=base_pd,
        grade=get_grade(base_pd),
        interest_rate=interest_rate,
        emi=emi,
        dti=dti,
        foir=foir,
        lti=lti,
        expected_loss=expected_loss,
        fico=fico,
        decision=decision,
        created_at=datetime.now(timezone.utc),
    )

    db.add(record)
    db.commit()

    # ── Response ──
    return {
        "status": decision,
        "summary": {
            "message": (
                "Loan Approved" if decision == "accept"
                else "Needs Review" if decision == "review"
                else "Rejected"
            ),
            "confidence": (
                "high" if base_pd < 0.2
                else "medium" if base_pd < 0.4
                else "low"
            ),
        },
        "financials": {
            "loan_amount": data.loan_amnt,
            "emi": round(emi, 2),
            "interest_rate": interest_rate,
            "dti": round(dti, 1),
        },
        "profile": {
            "monthly_income": monthly_income,
            "existing_emis": existing_emis,
        },
        "risk_metrics": {
            "pd": base_pd,
            "grade": get_grade(base_pd),
            "foir": round(foir, 2),
            "lti": round(lti, 2),
            "expected_loss": round(expected_loss, 2),
        },
        "insights": insights,
        "suggestions": suggestions,
        "alternatives": alternatives,
        "next_step": {
            "action":    "Find nearby branches",
            "map_query": f"{data.bank_name} bank near me",
        },    
    }

# ─────────────────────────────────
# HISTORY
# ─────────────────────────────────

@router.get("/history")
def loan_history(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    records = db.query(Risk).filter(
        Risk.customer_id == user_id
    ).order_by(Risk.created_at.desc()).limit(50).all()

    return {
        "total": len(records),
        "data": [
            {
                "bank": r.bank_name,
                "loan_amnt": r.loan_amnt,
                "decision": r.decision,
                "pd": r.adjusted_pd,
                "grade": r.grade,
                "emi": r.emi,
                "interest_rate": r.interest_rate,
                "dti": r.dti,
                "created_at": r.created_at,
            }
            for r in records
        ]
    }