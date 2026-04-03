from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session  # To identify the 'Session' type
import models                       # To identify 'models.Personnel'
from database import get_db          # If you need to use the database dependency
oauth2_scheme = HTTPBearer()


SECRET_KEY = "boohoo nigga"


ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password : str):
    return pwd_context.hash(password)

def verify_password(plain_password:str,hashed_password:str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return None
        return username

    except JWTError:
        # If token is invalid or expired — return None
        return None


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = verify_token(token.credentials)
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Check if user is blocked in the DB
    user = db.query(models.Personnel).filter(models.Personnel.username == username).first()
    if user and hasattr(user, 'is_blocked') and user.is_blocked == 1:
        raise HTTPException(
            status_code=403,
            detail="Account blocked due to suspicious activity"
        )
        
    return username
# This function protects any route you add it to
# def get_current_user(token: str = Depends(oauth2_scheme)):
#     username = verify_token(token)
#     if username is None:
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid or expired token"
#         )
#     return username
