from datetime import datetime, timedelta
from google import auth
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session  # To identify the 'Session' type
import models                       # To identify 'models.Personnel'
from database import get_db    

                                                 
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

# Use this as a dependency for Admin-only features
def verify_admin_access(current_user: models.Personnel = Depends(auth.get_current_user)):
    if current_user.role not in ['admin']:
        raise HTTPException(
            status_code=403, 
            detail="INSUFFICIENT CLEARANCE: Admin Privileges Required."
        )
    return current_user

def require_admin(current_user: models.Personnel = Depends(get_current_user)):
    # Check if the user's role is 'admin' or 'major'
    if current_user.role not in ['admin', 'major']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="INSUFFICIENT RANK: Command authority required."
        )
    return current_user
# This function protects any route you add it to
# def get_current_user(token: str = Depends(oauth2_scheme)):
#     username = verify_token(token)
#     if username is None:
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid or expired token"
#         )
#     return username
