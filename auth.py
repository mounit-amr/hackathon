from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBearer
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

# Tells FastAPI to look for token in Authorization header

def get_current_user(token: str = Depends(oauth2_scheme)):
    username = verify_token(token.credentials)
    if username is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
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
