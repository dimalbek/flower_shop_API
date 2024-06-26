from fastapi import (
    Cookie,
    FastAPI,
    Form,
    Request,
    Response,
    templating,
    Depends,
    HTTPException,
    Query,
)
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from typing import List
from pydantic import EmailStr

from .flowers_repository import (
    Flower,
    FlowersRepository,
    FlowerResponse,
    PatchFlowerRequest,
    FlowerRequest,
)
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
def get_profile(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    print("token:", token)
    user_id = decode_jwt(token)
    db_user = users_repository.get_by_id(db, int(user_id))
    return ProfileResponse(
        id=db_user.id, email=db_user.email, full_name=db_user.full_name
    )


@app.get("/flowers", response_model=List[FlowerResponse])
def get_flowers(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    flowers = flowers_repository.get_all(db, offset, limit)
    return flowers


@app.post("/flowers")
def post_flowers(
    flower: FlowerRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    flower_id = flowers_repository.save_flower(db, flower)
    return JSONResponse(
        status_code=200,
        content={"message": f"Flower with id {flower_id} successfully created"},
    )


@app.patch("/flowers/{flower_id}", response_model=FlowerResponse)
def patch_flower(
    flower_id: int,
    flower_data: PatchFlowerRequest,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    updated_flower = flowers_repository.update_flower(db, flower_id, flower_data)
    return updated_flower


@app.delete("/flowers/{flower_id}")
def delete_flower(
    flower_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    flower = flowers_repository.delete_flower(db, flower_id)
    return JSONResponse(
        status_code=200,
        content={"message": f"Flower with id {flower.id} successfully deleted"},
    )


def get_cart_items_from_cookie(request: Request):
    cart_items = request.cookies.get("cart_items")
    if not cart_items:
        return {}
    items = {}
    for item in cart_items.split(","):
        if ":" in item:
            flower_id, quantity = item.split(":")
            items[int(flower_id)] = int(quantity)
    return items


@app.post("/cart/items")
def add_flower_to_cookie(
    request: Request,
    response: Response,
    flower_id: int = Form(),
    quantity: int = Form(default=1),
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    if quantity < 1:
        return JSONResponse(
            content={"message": "Quantity should be greater than 0"},
            status_code=400
        )

    cart_items = get_cart_items_from_cookie(request)
    db_flower = flowers_repository.get_by_id(db, flower_id)
    if db_flower.count < quantity:
        return JSONResponse(
            content={"message": f"There are only {db_flower.count} flowers available"},
            status_code=400
        )

    cart_items[flower_id] = quantity
    cart_items_str = ",".join(f"{id}:{qty}" for id, qty in cart_items.items())

    response = JSONResponse(
        content={"message": "Flower added to cart"}, status_code=200
    )
    response.set_cookie(
        key="cart_items",
        value=cart_items_str,
        httponly=True,
        max_age=1800,
        path="/",
    )
    return response


@app.get("/cart/items")
def get_cart_items(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    cart_items = get_cart_items_from_cookie(request)
    flowers_in_cart = []
    total_cost = 0

    for flower_id_str, quantity in cart_items.items():
        flower_id = int(flower_id_str)
        flower = flowers_repository.get_by_id(db, flower_id)
        if flower:
            flowers_in_cart.append(
                {
                    "id": flower.id,
                    "name": flower.name,
                    "cost": flower.cost,
                    "quantity": quantity,
                }
            )
            total_cost += flower.cost * quantity

    return JSONResponse(
        content={"flowers_in_cart": flowers_in_cart, "total_cost": total_cost}
    )
