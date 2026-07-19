from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class ExpenseCreate(BaseModel):
    """Data the CLIENT is allowed to send when creating an expense."""
    amount: Decimal = Field(gt=0)
    description: str = Field(min_length=1, max_length=255)
    # add your other client-supplied columns here to match models.py

class ExpenseRead(BaseModel):
    """Data the SERVER send back - includes DB-generated fields."""
    id: int
    amount: Decimal
    description: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)  # tells Pydantic to read data from ORM objects

    