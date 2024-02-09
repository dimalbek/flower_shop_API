from attrs import define


@define
class User:
    email: str
    full_name: str
    id: int = 0


class UsersRepository:
    users: list[User]

    def __init__(self):
        self.users = []

    # необходимые методы сюда

    # конец решения
