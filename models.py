from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid

from db import Base, engine

class Registration(Base):
    __tablename__ = "registration"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(Integer, unique=True, nullable=False, index=True)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    password = Column(String, nullable=False)

    is_verified = Column(Boolean, default=False)   # 🔥 ONLY ONE FLAG
    registered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))




class Risk(Base):
    __tablename__ = "risk"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id   = Column(Integer, nullable=False, index=True)
    bank_name     = Column(String, nullable=False)
    loan_amnt     = Column(Float, nullable=False)
    annual_inc    = Column(Float, nullable=False)   # auto-derived: monthly * 12

    # ML output
    base_pd       = Column(Float, nullable=False)
    adjusted_pd   = Column(Float, nullable=False)
    grade         = Column(String, nullable=False)  # A-F from adjusted_pd

    # Financials
    interest_rate = Column(Float, nullable=False)   # Float (SQLAlchemy), not float (Python)
    emi           = Column(Float, nullable=False)
    dti           = Column(Float, nullable=False)   # debt-to-income %
    foir          = Column(Float, nullable=False)   # fixed obligation ratio
    lti           = Column(Float, nullable=False)   # loan-to-income
    expected_loss = Column(Float, nullable=False)
    fico          = Column(Integer, nullable=False)  # derived credit score

    # Decision
    decision      = Column(String, nullable=False)  # accept / review / reject

    created_at    = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(Integer, nullable=False, index=True)
    token_hash  = Column(String, nullable=False)
    expire      = Column(DateTime(timezone=True), nullable=False)


class FinancialProfile(Base):
    __tablename__ = "financial_profile"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id         = Column(Integer, nullable=False, index=True)
    employment_type     = Column(String, nullable=False)
    years_of_experience = Column(Integer, nullable=False, default=0)
    monthly_income      = Column(Float, nullable=False, default=0.0)
    monthly_expenses    = Column(Float, nullable=False, default=0.0)
    existing_emis       = Column(Float, nullable=False, default=0.0)
    updated_at          = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class OTP(Base):
    __tablename__ = "otp"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    customer_id = Column(Integer, nullable=False, index=True)
    email = Column(String, nullable=False)

    otp_hash = Column(String, nullable=False)
    purpose = Column(String, nullable=False)  # verify | reset

    expire_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)

    attempts = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))



