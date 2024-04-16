from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .models import User
from attrs import define
from pydantic import BaseModel, EmailStr

@define
class UserCreate:
    email: str
    full_name: str
    password: str


class ProfileResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str

class UsersRepository:

    def save(self, db: Session, user_data: UserCreate) -> User:
        try:
            # Check if the user already exists
            existing_user = db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="User already exists")

            new_user = User(
                email=user_data.email,
                full_name=user_data.full_name,
                password=user_data.password,
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="User already exists")

    def get_by_email(self, db: Session, email: str) -> User:
        db_user = db.query(User).filter(User.email == email).first()
        if db_user is None:
            print(f"User with email {email} not found") 
            raise HTTPException(status_code=404, detail="User not found")
        return db_user

    def get_by_id(self, db: Session, user_id: int) -> User:
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user
