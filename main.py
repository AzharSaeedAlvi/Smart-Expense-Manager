from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.orm import Session


from database import get_db
from models import Expense
from schemas import ExpenseCreate, ExpenseRead, ExpenseUpdate

from typing import List 
from sqlalchemy import select

#Phase 3 imports

from models import User
from schemas import UserCreate, UserRead
from security import hash_password

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

#We deliberately use PATCH instead of PUT because we want to allow partial updates. If we use PUT, then it will automatically remove every field that the client did not send. PATCH allows us to only update the fields that the client sent.

@app.patch("/expenses/{expense_id}", response_model=ExpenseRead)
def update_expense(expense_id: int, payload: ExpenseUpdate, db: Session = Depends(get_db)):
    expense = db.get(Expense, expense_id)
    if expense is None: 
        raise HTTPException(status_code=404, detail="Expense not found")

    update_data= payload.model_dump(exclude_unset=True)    #Give me a dict of only the fields that the client sent.
    for field, value in update_data.items():
        setattr(expense, field, value)


    db.commit()
    db.refresh(expense)
    return expense

@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.get(Expense, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    db.commit()
    return None



#Adding the Phase 3 section 

@app.post("/auth/reg", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.scalars(select(User).where(User.email == payload.email)).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="Email already registered")


    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user