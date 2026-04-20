from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Literal, Optional


# -------------------------------
# AUTH SCHEMAS
# -------------------------------

class Register(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class Verify(BaseModel):
    token: str


class RefreshRequest(BaseModel):
    refresh_token: str


# -------------------------------
# LOAN SCHEMA
# Customer provides only these 4 fields.
# Everything else is derived from profile.
# -------------------------------

class LoanRequest(BaseModel):
    loan_amnt: float = Field(ge=10000, le=10_000_000, description="Loan amount in INR")
    term: Literal["36 months", "60 months"]
    purpose: Literal[
        "debt_consolidation", "credit_card", "home_improvement",
        "other", "major_purchase", "medical", "small_business",
        "car", "vacation", "moving", "house", "wedding", "educational"
    ]
    bank_name: str


# -------------------------------
# FINANCIAL PROFILE SCHEMA
# Typo fixed: "Bussiness" → "business"
# All values normalized to lowercase_underscore
# to match EMPLOYMENT_FACTOR keys in loan.py
# -------------------------------

class FinancialProfileCreate(BaseModel):
    employment_type: Literal[
        "business",
        "it_employer",
        "govt_employer",
        "non_it_employer",
        "student"
    ]
    years_of_experience: Optional[int] = Field(default=None, ge=0, le=50)
    monthly_income: Optional[float] = Field(default=None, ge=0)
    monthly_expenses: Optional[float] = Field(default=None, ge=0)
    existing_emis: Optional[float] = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_non_student_fields(self):
        if self.employment_type != "student":
            if self.monthly_income is None or self.monthly_income <= 0:
                raise ValueError("monthly_income is required and must be > 0 for non-students")
            if self.years_of_experience is None:
                raise ValueError("years_of_experience is required for non-students")
            if self.monthly_expenses is None:
                raise ValueError("monthly_expenses is required for non-students")
            if self.existing_emis is None:
                raise ValueError("existing_emis is required for non-students")
        return self
class SendOTP(BaseModel):
    email: EmailStr
    purpose: Literal["signup", "reset"]


class VerifyOTP(BaseModel):
    email: EmailStr
    otp: str
    purpose: str

class Login(BaseModel):
    customer_id: int
    password: str

class Refresh(BaseModel):
    refresh_token: str