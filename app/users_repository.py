from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .models import User
from attrs import define


@define
class UserCreate:
    email: str
    full_name: str
    password: str


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
            raise HTTPException(status_code=404, detail="User not found")
        return db_user

    def get_by_id(self, db: Session, user_id: int) -> User:
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user


# from pydantic import BaseModel


# class User(BaseModel):
#     email: str
#     full_name: str
#     password: bytes
#     id: int = 0


# class UsersRepository:
#     users: list[User]

#     def __init__(self):
#         self.users = []

#     # необходимые методы сюда
#     def get_all(self):
#         return self.users

#     def get_one(self, id):
#         for user in self.users:
#             if id == user.id:
#                 return user
#         return None

#     def save(self, user: User):
#         user.id = len(self.users) + 1
#         self.users.append(user)
#         return user

#     def update(self, id: int, input: User):
#         for i, user in enumerate(self.users):
#             if user.id == id:
#                 input.id = id
#                 self.users[i] = input

#     def delete(
#         self,
#         id: int,
#     ):
#         for i, user in enumerate(self.users):
#             if user.id == id:
#                 del self.users[i]

#     def check_user(self, email: str, password: bytes):
#         for user in self.users:
#             if user.email == email:
#                 if user.password == password:
#                     return user

#         return None

#     def get_user_by_email(self, email: str):
#         for user in self.users:
#             if email == user.email:
#                 return user
#         return None

#     # конец решения
