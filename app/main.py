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


# конец решения
