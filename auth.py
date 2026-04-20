from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
import uuid, hashlib, secrets, os, logging
from fastapi import HTTPException, Depends
from models import RefreshToken
from sqlalchemy.orm import Session
from db import get_db
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/predictions.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

SECRET_KEY = os.getenv("SECURITY_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECURITY_KEY not set in .env")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
security = HTTPBearer()


def hash_password(password: str):
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=400,
            detail="Password too long. Max allowed is 72 bytes."
        )

    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def generate_customer_id(db: Session) -> int:
    """Generate a unique customer ID with collision retry loop."""
    from models import Registration
    for _ in range(10):
        cid = secrets.randbelow(10**9 - 100000) + 100000  # 6-9 digit IDs
        exists = db.query(Registration).filter(Registration.customer_id == cid).first()
        if not exists:
            return cid
    raise RuntimeError("Could not generate a unique customer ID after 10 attempts")


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(customer_id: int) -> str:
    payload = {
        "sub": str(customer_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(customer_id: int, db: Session) -> str:
    raw = str(uuid.uuid4())
    db_token = RefreshToken(
        customer_id=customer_id,
        token_hash=hash_token(raw),
        expire=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(db_token)
    db.commit()
    return raw


def verify_refresh_token(token: str, db: Session):
    hashed = hash_token(token)
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == hashed
    ).first()
    if not db_token:
        return None
    # timezone-aware comparison
    expire = db_token.expire
    if expire.tzinfo is None:
        expire = expire.replace(tzinfo=timezone.utc)
    if expire < datetime.now(timezone.utc):
        db.delete(db_token)
        db.commit()
        return None
    return db_token


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        customer_id = payload.get("sub")
        if customer_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return int(customer_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
