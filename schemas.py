from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class ExpenseCreate(BaseModel):
    """Data the CLIENT is allowed to send when creating an expense."""
    amount: Decimal = Field(gt=0)
    description: str = Field(min_length=1, max_length=255)
    spent_on: date
    # add your other client-supplied columns here to match models.py

class ExpenseRead(BaseModel):
    """Data the SERVER send back - includes DB-generated fields."""
    id: int
    amount: Decimal
    description: str
    created_at: datetime
    updated_at: datetime
    spent_on: date        #added this for a fix. 
    model_config = ConfigDict(from_attributes=True)  # tells Pydantic to read data from ORM objects


class ExpenseUpdate(BaseModel):
        amount: Decimal | None = Field(default=None, gt=0, max_digits=10)          #NONE makes it optional
        description: str | None = Field(default=None, min_length=1, max_length=255)
        spent_on: date | None = None


#Phase 3

class UserCreate(BaseModel):
     """"What a client sends to register"""

     name: str = Field(min_length=1, max_length=100)
     email: str
     password: str = Field(min_length=8)


class UserRead(BaseModel):
     """What server sends back - no password, no hash, ever."""
     """The reason it will not read .hashed_password, is because UserRead doesn't have hash present which is present in the user_object under models"""


     id: int
     name: str
     email: str
     created_at: datetime

     model_config = ConfigDict(from_attributes=True)

