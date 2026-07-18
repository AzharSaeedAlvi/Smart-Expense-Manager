from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import String, DateTime, Numeric, Date, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    "Shared parent for every table-class in this project."
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Lets you write 'some_user.expenses' in Python

    expenses: Mapped[list["Expense"]] = relationship(back_populates="user")

    class Expense(Base):
        __tablename__ = "expenses"

        id: Mapped[int] = mapped_column(primary_key=True)
        amount: Mapped[Decimal] = mapped_column(Numeric(10,2))
        description: Mapped[str] = mapped_column(String(255))
        spent_on: Mapped[date] = mapped_column(Date)
        user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

        created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), server_default=func.now()
        )
        updated_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
        )

        #Lets you write 'some_expense.user' in Python

        user: Mapped[list["User"]] = relationship(back_populates="expenses")
