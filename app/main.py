from fastapi import (
    Cookie,
    FastAPI,
    Form,
    Request,
    Response,
    templating,
    Depends,
    HTTPException,
)
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from typing import List
from pydantic import EmailStr

from .flowers_repository import Flower, FlowersRepository
from .users_repository import User, UsersRepository, UserCreate, ProfileResponse
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .database import get_db

app = FastAPI()
templates = templating.Jinja2Templates("templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt(user_id: int) -> str:
    body = {"user_id": user_id}
    token = jwt.encode(body, "nfac_secret", "HS256")
    return token


def decode_jwt(token: str) -> int:
    data = jwt.decode(token, "nfac_secret", "HS256")
    return data["user_id"]


flowers_repository = FlowersRepository()
users_repository = UsersRepository()


@app.post("/signup")
def post_signup(
    email: EmailStr = Form(),
    full_name: str = Form(),
    password: str = Form(),
    db: Session = Depends(get_db),
):
    password = hash_password(password)
    user = UserCreate(email=email, full_name=full_name, password=password)
    new_user = users_repository.save(db, user)
    return Response(
        status_code=200, content=f"successfull signup. User_id = {new_user.id}"
    )


@app.post("/login")
def post_login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = users_repository.get_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        # return {"form": hash_password(form_data).password, "db": user.password}
        raise HTTPException(
            status_code=401,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_jwt(user.id)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/profile", response_model=ProfileResponse)
def get_profile(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    print("token:", token)
    user_id = decode_jwt(token)
    db_user = users_repository.get_by_id(db, int(user_id))
    return ProfileResponse(
        id=db_user.id,
        email=db_user.email,
        full_name=db_user.full_name
    )




@app.get("/flowers", response_model=List[Flower])
def get_flowers():
    return flowers_repository.get_all()


@app.post("/flowers", response_model=Flower)
def add_flower(name: str = Form(), count: int = Form(), cost: int = Form()):
    flower_data = Flower(name=name, count=count, cost=cost)
    saved_flower = flowers_repository.save(flower_data)
    return saved_flower


def get_cart_items_from_cookie(request: Request):
    cart_items = request.cookies.get("cart_items")
    if cart_items is None:
        return []
    cart = cart_items.split()
    return cart


@app.post("/cart/items")
def add_flower_to_cookie(
    request: Request,
    response: Response,
    flower_id: int = Form(),
):
    cart_items = get_cart_items_from_cookie(request)
    cart_items.append(str(flower_id))
    cart_items_str = ",".join([str(item) for item in cart_items])
    response.set_cookie("cart_items", cart_items_str)
    return JSONResponse(content={"message": "flower added to cart"}, status_code=200)


@app.get("/cart/items")
def get_cart_items(request: Request):
    cart_items = get_cart_items_from_cookie(request)
    flowers_in_cart = []
    total_cost = 0

    for flower_id in cart_items:
        flower_id = int(flower_id)
        flower = flowers_repository.get_one(flower_id)
        if flower:
            flowers_in_cart.append(
                {"id": flower.id, "name": flower.name, "cost": flower.cost}
            )
            total_cost += flower.cost

    return JSONResponse(
        content={"flowers_in_cart": flowers_in_cart, "total_cost": total_cost}
    )
