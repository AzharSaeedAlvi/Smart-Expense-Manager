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

from fastapi.security import OAuth2PasswordRequestForm
from schemas import Token
from security import   verify_password, create_access_token


#Phase 3 : Dependency 

import  jwt
from fastapi.security import OAuth2PasswordBearer
from security import decode_access_token

app = FastAPI()

   # Phase 3 Dependency : This needs to be at the top, as this will help us in authorizing the valuse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "auth/login")

def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials ",
        headers= {"WWW-Authenticate" : "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = db.get(User,  int(user_id))
    if user is None:
        raise credentials_exception
    return user

# DEV_USER_ID = 5  #TEMP: Phase 3 replaces this with the authenticated user

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/expenses", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    expense = Expense(**payload.model_dump(), user_id=current_user.id)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


## This was used when we did not have authorization setup. We used a pre-created DEV_USER to store exepnses
# def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db)):
#     expense = Expense(**payload.model_dump(), user_id=DEV_USER_ID) # Assuming DEV_USER_ID is defined in seed_dev_user.py
#     db.add(expense)          # Stages the row
#     db.commit()              # Writes it to DB
#     db.refresh(expense)      # Re-reads it so the DB generated files gets populated in your object. 
#     return expense           # Converts : raw SQLAlchemy object, response_model and from_attributes=True into clean JSON.


@app.get("/expenses", response_model=List[ExpenseRead])
def list_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expenses = db.scalars(
        select(Expense).where(Expense.user_id == current_user.id)
    ).all()
    return expenses

#The above can be read as: Hi, look into the database, get the Expense object and then compare the Expense.user_id object with current_user.id and if it matches return all the expenses, if you would only like 1 expense run .first() instead of .all()


#Commenting this out as this is works even without authorization
# def list_expenses(db: Session = Depends(get_db)):
#     return db.scalars(select(Expense)).all()

#This will ensure that that only if the User id and owner matches only then it works.

@app.get("/expenses/{expense_id}", response_model=ExpenseRead)
def get_one_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = db.scalars(
        select(Expense).where(
            Expense.id == expense_id,
            Expense.user_id == current_user.id,
        )
    ).first()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense
    


#Removed this as it was pulling expense for all the users without any restrictions.
    # @app.get("/expenses/{expense_id}", response_model=ExpenseRead)
    # def get_expense(expense_id: int, db: Session = Depends(get_db)):
    #     expense = db.get(Expense, expense_id)
    #     if expense is None:
    #         raise HTTPException(status_code=404, detail="Expense Not Found")
    #     return expense

#We deliberately use PATCH instead of PUT because we want to allow partial updates. If we use PUT, then it will automatically remove every field that the client did not send. PATCH allows us to only update the fields that the client sent.

@app.patch("/expenses/{expense_id}", response_model=ExpenseRead)
def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = db.scalars(
        select(Expense).where(                           #Ensuring that both the Expense id and User id mathces for the person requesting the update.
            Expense.id == expense_id,
            Expense.user_id == current_user.id,
        )
    ).first()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(expense, field, value)  

    db.commit()
    db.refresh(expense)
    return expense

# Commenting this out as this code works without Authorization, so in the code above we have added a Fetch by id AND owner first condition.
# @app.patch("/expenses/{expense_id}", response_model=ExpenseRead)
# def update_expense(expense_id: int, payload: ExpenseUpdate, db: Session = Depends(get_db)):
#     expense = db.get(Expense, expense_id)
#     if expense is None: 
#         raise HTTPException(status_code=404, detail="Expense not found")

#     update_data= payload.model_dump(exclude_unset=True)    #Give me a dict of only the fields that the client sent.
#     for field, value in update_data.items():
#         setattr(expense, field, value)


    db.commit()
    db.refresh(expense)
    return expense

@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = db.scalars(
        select(Expense).where(
            Expense.id == expense_id,
            Expense.user_id == current_user.id,
        )
    ).first()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not Found")

    db.delete(expense)               ## We have subtly included this under the loop, this will ensure that it only reaches the point when the user has been authorized, else it would have thrown the error even before entorring the loop
    db.commit()

# Commenting this out as this code works without Authorization, so in the code above we have added a Fetch by id AND owner first condition.
# @app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_expense(expense_id: int, db: Session = Depends(get_db)):
#     expense = db.get(Expense, expense_id)
#     if expense is None:
#         raise HTTPException(status_code=404, detail="Expense not found")

#     db.delete(expense)
#     db.commit()
#     return None



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


#Phase 3 : Endpoint setup

@app.post("/auth/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    user = db.scalars(select(User).where(User.email == form_data.username)).first()
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code= 401,
            detail = "Incorrect email or password",
            headers={"WWW-Authenticate" : "Bearer"},
        )

    access_token = create_access_token(subject=str(user.id))
    return {"access_token": access_token, "token_type": "bearer"}
    


 


@app.get("/auth/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user