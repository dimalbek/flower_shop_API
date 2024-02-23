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

from .flowers_repository import Flower, FlowersRepository
from .purchases_repository import Purchase, PurchasesRepository
from .users_repository import User, UsersRepository
from passlib.context import CryptContext


# def hash_password(password: str):
#     h = 0
#     for char in password:
#         h = (31 * h + ord(char)) & 0xFFFFFFFF
#     return bytes(((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000)


app = FastAPI()
templates = templating.Jinja2Templates("templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
purchases_repository = PurchasesRepository()
users_repository = UsersRepository()


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/signup")
def display_signup(request: Request):
    return templates.TemplateResponse("users/signup.html", {"request": request})


@app.post("/signup")
def post_signup(
    request: Request,
    email: str = Form(),
    full_name: str = Form(),
    password: str = Form(),
):
    password = hash_password(password)
    user = User(email=email, full_name=full_name, password=password)
    users_repository.save(user)
    return JSONResponse(content={"message": "successfull signup"}, status_code=200)


@app.get("/login")
def display_login(request: Request):
    return templates.TemplateResponse("users/login.html", {"request": request})


@app.post("/login")
def post_login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_repository.get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_jwt(user_id=user.id)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/profile")
def get_profile(token: str = Depends(oauth2_scheme)):
    user_id = decode_jwt(token)
    user = users_repository.get_one(int(user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.dict(exclude={"password"})
    return user_data


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
