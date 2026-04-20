
# LoanIQ — Credit Risk Platform

An AI-powered full-stack credit risk assessment system built using **FastAPI, LightGBM, PostgreSQL, and JWT authentication**.  
The platform evaluates loan applications, predicts default risk, and provides real-time financial insights with a secure OTP-based onboarding system.

---

## 🚀 Features

### 🔐 Authentication System
- JWT-based login & refresh token system
- OTP email verification (signup + password reset)
- Secure password hashing (bcrypt)

### 🧠 Machine Learning Engine
- LightGBM model for credit risk prediction
- Feature pipeline using scikit-learn
- Predicts:
  - Default risk probability
  - Loan approval decision (Accept / Review / Reject)
  - Interest rate & EMI estimation

### 🏦 Loan Risk System
- Real-time loan evaluation
- Bank-specific risk adjustment
- Debt-to-income (DTI) & FOIR calculations
- Expected loss estimation

### 📊 Financial Profile System
- User financial profiling (income, expenses, EMIs)
- Employment-based risk weighting
- Profile-driven loan decisions

### 🌐 Full-Stack Application
- FastAPI backend (REST APIs)
- HTML/CSS/JavaScript frontend
- Real-time API integration
- Dockerized deployment

### 🗄️ Database
- PostgreSQL with SQLAlchemy ORM
- Persistent user profiles & loan history
- OTP tracking system

---

## 🏗️ Tech Stack

**Backend:**
- FastAPI
- SQLAlchemy
- Pydantic v2
- JWT (OAuth2 Password Flow)
- Passlib (bcrypt)

**ML:**
- LightGBM
- Scikit-learn pipeline
- Pandas, NumPy

**Database:**
- PostgreSQL

**Frontend:**
- HTML5
- CSS3
- Vanilla JavaScript

**DevOps:**
- Docker
- Docker Compose
- AWS EC2 Deployment

---

## 📂 Project Structure


backend/
│
├── main.py
├── db.py
├── models.py
├── schemas.py
├── auth.py
├── otp_service.py
├── email_service.py
├── ml.py
│
├── router/
│ ├── reg.py
│ ├── login.py
│ ├── verify.py
│ ├── refresh.py
│ ├── profile.py
│ ├── loan.py
│
├── static/
│ └── index.html
│
├── model.pkl
├── features.pkl
└── logs/


---

## ⚙️ Setup Instructions

### 1. Clone Repository

git clone https://github.com/your-username/loaniq-credit-risk-platform.git
cd loaniq-credit-risk-platform
2. Run with Docker
docker compose up --build -d
3. Access Application
Frontend: http://localhost:8000/
API Docs: http://localhost:8000/docs
🔗 API Endpoints
Auth
POST /auth/register → Register user + send OTP
POST /auth/verify → Verify OTP
POST /auth/login → Login user
POST /auth/refresh → Refresh token
Profile
POST /profile/ → Create profile
GET /profile/ → Get profile
Loan
POST /loan/ → Risk prediction
GET /loan/history → Loan history
📊 ML Model Output

The system returns:

Loan Decision: Accept / Review / Reject
Interest Rate (%)
EMI Calculation
Debt-to-Income Ratio (DTI)
Risk Probability Score
Alternative Bank Suggestions
🚀 Deployment

Deployed on AWS EC2 using Docker:

Ubuntu 24.04 LTS
Docker + Docker Compose
Nginx-ready structure (optional upgrade)
🧠 Key Highlights
End-to-end credit risk system
Real-world banking logic simulation
Production-style authentication system
ML + backend integration (not just notebook project)
Scalable microservice-ready architecture
📌 Future Improvements
React frontend upgrade
Redis caching for OTP
Microservices split (Auth / ML / Loan engine)
CI/CD pipeline (GitHub Actions)
HTTPS with Nginx + domain
