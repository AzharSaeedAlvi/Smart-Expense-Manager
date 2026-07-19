import os

from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker

from collections.abc import Generator
from sqlalchemy.orm import Session



#Single source of truth for where the database lives. 
#Local dev falls back to a SQLite file; production overrides this with a real env var. 

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./expenses.db")


#check_same_thread is a SQLite-only quirk; it's needed once FastAPI touches the DB across threads.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else{}

#echo=True prints the SQL SQLAlchemy generates - Leave it on while Learning. 
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)




#Phase 2

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()
        