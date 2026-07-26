from passlib.context import CryptContext

#Adding config block from Phase 3

import os 
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

# PHASE 3 

load_dotenv()    #This must be read before anything else to ensure it runs before any variable is read. 

SECRET_KEY = os.environ["SECRET_KEY"]    # Explicitly used [] instead of .get() as we want it to fail loudly at start up  [Fail Fast on misconfiguration - Principle]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload= {"sub": subject, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


#A decoded helper : Phase 3   // Check signature and exp

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


