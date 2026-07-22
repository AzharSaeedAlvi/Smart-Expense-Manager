from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.orm import Session


from database import get_db
from models import Expense
from schemas import ExpenseCreate, ExpenseRead

from typing import List 
from sqlalchemy import select

app = FastAPI()

DEV_USER_ID = 5  #TEMP: Phase 3 replaces this with the authenticated user

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/expenses", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db)):
    expense = Expense(**payload.model_dump(), user_id=DEV_USER_ID) # Assuming DEV_USER_ID is defined in seed_dev_user.py
    db.add(expense)          # Stages the row
    db.commit()              # Writes it to DB
    db.refresh(expense)      # Re-reads it so the DB generated files gets populated in your object. 
    return expense           # Converts : raw SQLAlchemy object, response_model and from_attributes=True into clean JSON.


@app.get("/expenses", response_model=List[ExpenseRead])
def list_expenses(db: Session = Depends(get_db)):
    return db.scalars(select(Expense)).all()

@app.get("/expenses/{expense_id}", response_model=ExpenseRead)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.get(Expense, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense Not Found")
    return expense