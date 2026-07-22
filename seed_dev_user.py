from sqlalchemy import select
from database import SessionLocal
from models import User 

DEV_EMAIL = "dev@example.com"


db = SessionLocal()
user = db.scalars(select(User).where(User.email == DEV_EMAIL)).first()
if user is None:
    user = User(email=DEV_EMAIL, name="Dev User")     # add your other NOT NULL fields here
    db.add(user)
    db.commit()
    db.refresh(user)
    print("Created dev user.")
else:
    print("Dev user already exists.")
print("DEV_USER_ID =", user.id)
db.close()

