from fastapi import Cookie, FastAPI, Form, Request, Response, templating
from fastapi.responses import RedirectResponse
from jose import jwt

from .flowers_repository import Flower, FlowersRepository
from .purchases_repository import Purchase, PurchasesRepository
from .users_repository import User, UsersRepository
import bcrypt


def hash_password(password: str):
    password = b"{password}"
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return hashed


app = FastAPI()
templates = templating.Jinja2Templates("templates")


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


# ваше решение сюда
@app.get("/signup")
def display_signup(request: Request):
    return templates.TemplateResponse("users/signup.html", {"request": request})


@app.post("/signup")
def post_signup(
    request: Request,
    email: str = Form(),
    fullname: str = Form(),
    password: str = Form(),
):
    password = hash_password(password)

    user = User(email=email, full_name=fullname, password=password)
    users_repository.save(user)

    # return {'succesful signup'}
    return RedirectResponse("/login", status_code=303)


@app.get("/login")
def display_login(request: Request):
    return templates.TemplateResponse("users/login.html", {"request": request})


@app.post("/signup")
def post_login(
    request: Request,
    email: str = Form(),
    password: str = Form(),
):
    password = hash_password(password)
    user = users_repository.check_user(email, password)
    if user is None:
        return Response(status_code=401, content="Not authorized")

    response = RedirectResponse("/profile", status_code=303)
    token = create_jwt(user.id)
    response.set_cookie("token", token)
    return response


# конец решения
