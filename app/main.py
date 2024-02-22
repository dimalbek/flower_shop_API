from fastapi import Cookie, FastAPI, Form, Request, Response, templating
from fastapi.responses import RedirectResponse
from jose import jwt

from .flowers_repository import Flower, FlowersRepository
from .purchases_repository import Purchase, PurchasesRepository
from .users_repository import User, UsersRepository


def hash_password(password: str):
    h = 0
    for char in password:
        h = (31 * h + ord(char)) & 0xFFFFFFFF
    return bytes(((h + 0x80000000) & 0xFFFFFFFF) - 0x80000000)


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
    full_name: str = Form(),
    password: str = Form(),
):
    password = hash_password(password)
    # print (password)

    user = User(email=email, full_name=full_name, password=password)
    users_repository.save(user)

    # return {'succesful signup'}
    return RedirectResponse("/login", status_code=303)


@app.get("/login")
def display_login(request: Request):
    return templates.TemplateResponse("users/login.html", {"request": request})


@app.post("/login")
def post_login(
    request: Request,
    response: Response,
    email: str = Form(),
    password: str = Form(),
):
    password = hash_password(password)
    # print (password)
    user = users_repository.check_user(email, password)
    if user is None:
        return Response(status_code=401, content="Not authorized")

    response = RedirectResponse("/profile", status_code=303)
    token = create_jwt(user.id)
    response.set_cookie("token", token)
    return response


@app.get("/profile")
def get_profile(request: Request, token: str = Cookie(default="")):
    if token == "":
        return RedirectResponse("/login", status_code=303)
    user_id = decode_jwt(token)
    user = users_repository.get_one(int(user_id))
    if user is None:
        return Response(status_code=401, content="Not authorized")

    return templates.TemplateResponse(
        "users/profile.html", {"request": request, "user": user}
    )


@app.get("/flowers")
def get_flowers(request: Request):
    flowers = flowers_repository.get_all()
    return templates.TemplateResponse(
        "flowers/flowers.html", {"request": request, "flowers": flowers}
    )


@app.post("/flowers")
def add_flower(
    request: Request,
    name: str = Form(),
    count: str = Form(),
    cost: str = Form()
):
    flower = Flower(name=name, count=count, cost=cost)
    flowers_repository.save(flower)
    return RedirectResponse("/flowers", status_code=303)


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
    flower_id: str = Form(),
):
    cart_items = get_cart_items_from_cookie(request)
    cart_items.append(flower_id)
    cart_items_str = ",".join([str(item) for item in cart_items])
    response.set_cookie("cart_items", cart_items_str)
    return RedirectResponse("/flowers", status_code=303)



# конец решения
