from fastapi import Cookie, FastAPI, Form, Request, Response, templating
from fastapi.responses import RedirectResponse

from .flowers_repository import Flower, FlowersRepository
from .purchases_repository import Purchase, PurchasesRepository
from .users_repository import User, UsersRepository

app = FastAPI()
templates = templating.Jinja2Templates("templates")


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
def post_book(
    request: Request,
    email: str = Form(),
    fullname: str = Form(),
    password: str = Form(),
):
    user = User(email=email, fullname=fullname, password=password)
    users_repository.save(user)

    return RedirectResponse("/login", status_code=303)

# конец решения
