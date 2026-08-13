import csv
import io
from fastapi.responses import StreamingResponse, JSONResponse

from fastapi.middleware.cors import CORSMiddleware

import logging
import uuid
from fastapi import Request

logger = logging.getLogger("expense-api")

from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.orm import Session


from database import get_db
from models import Expense
from schemas import (
ExpenseCreate, ExpenseRead, ExpenseUpdate, MonthlyTotalRead, MonthOverMonthRead
)

from categorization import default_categorizer

from datetime import date

from typing import List 
from sqlalchemy import select, func

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

app.add_middleware(
    CORSMiddleware,
    allow_origins= ["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    error_id = uuid.uuid4().hex[:8]
    logger.exception(
        "Unhandled error [%s] on %s %s", error_id, request.method, request.url.path
      )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error_id": error_id},
     
    )


    
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

def get_month_boundaries(
        reference_date: date,
) -> tuple[date, date, date]:
    current_start = reference_date.replace(day=1)

    if current_start.month == 1:
        previous_start = date(current_start.year - 1, 12, 1)
    else:
        previous_start = date(
            current_start.year,
            current_start.month - 1,
            1,
        )
    if current_start.month == 12:
        next_start = date(current_start.year + 1, 1, 1)
    else:
        next_start = date(
            current_start.year,
            current_start.month + 1,
            1,
        )

    return previous_start, current_start, next_start

@app.get("/health")
def health_check():
    return{"status": "ok"}


@app.post("/expenses", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    data = payload.model_dump()
    if data.get("category") is None:
            data["category"] = default_categorizer.categorize(data["description"])
    expense = Expense(**data, user_id=current_user.id)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


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


@app.get("/insights/monthly-total", response_model=MonthlyTotalRead)
def get_monthly_total(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    _, month_start, next_month_start = get_month_boundaries(date.today())   #Helper function.

    # today = date.today()           #Pulls in backend's machine date. 
    # month_start = today.replace(day=1)

    # if today.month == 12:
    #     next_month_start = date(today.year + 1, 1, 1)
    # else:
    #     next_month_start = date(today.year, today.month + 1, 1)

    total = db.scalar(
        select(func.coalesce(func.sum(Expense.amount), 0)).where(
            Expense.user_id == current_user.id,
            Expense.spent_on >= month_start,
            Expense.spent_on < next_month_start,
        )
    )

    return {"total": total}


@app.get("/insights/month-over-month", 
         response_model=MonthOverMonthRead,
)
def get_month_over_month(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    previous_start, current_start, next_start = get_month_boundaries(
        date.today()
    )

    previous_total = db.scalar(
        select(func.coalesce(func.sum(Expense.amount), 0)).where(
            Expense.user_id == current_user.id,
            Expense.spent_on >= previous_start,
            Expense.spent_on < current_start,
        )
    )

    current_total = db.scalar(
        select(func.coalesce(func.sum(Expense.amount), 0)).where(
            Expense.user_id == current_user.id,
            Expense.spent_on >= current_start, 
            Expense.spent_on < next_start,

        )
    )

    change_amount = current_total - previous_total

    change_percentage = None
    if previous_total !=0:
        change_percentage = round(
            (change_amount/previous_total)* 100,
            2,
        )

    return {
        "current_month_total": current_total,
        "previous_month_total": previous_total,
        "change_amount": change_amount,
        "change_percentage": change_percentage,
    }

def _expenses_in_range(
    start: date,
    end: date,
    db: Session,
    current_user: User,
) -> list[Expense]:
    if start>end:
        raise HTTPException(
            status_code=400,
            detail= "Start date must be on or before end date",
        )
    return db.scalars(
        select(Expense).where(
            Expense.user_id == current_user.id,
            Expense.spent_on >= start,
            Expense.spent_on <= end,
        )
    ).all()

@app.get("/reports/monthly", response_model=List[ExpenseRead])
def get_monthly_report(
    start: date,
    end: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return _expenses_in_range(start, end, db, current_user)


@app.get("/reports/monthly.csv")
def export_monthly_report_csv(
    start: date,
    end: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    expenses = _expenses_in_range(start, end, db, current_user)

    buffer = io.StringIO()
    writer= csv.writer(buffer)
    writer.writerow(["id", "description","category", "amount", "spent_on"])
    for expense in expenses:
        writer.writerow(
            [expense.id, expense.description, expense.category, expense.amount, expense.spent_on]
        )
    buffer.seek(0)

    filename = f"expenses_{start}_{end}.csv"
    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )



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


    # db.commit()
    # db.refresh(expense)
    # return expense

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

@app.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
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