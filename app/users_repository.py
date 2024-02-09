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
    def get_all(self):
        return self.users

    def get_one(self, id):
        for user in self.users:
            if id == user.id:
                return user
        return None

    def save(self, user: User):
        user.id = len(self.users) + 1
        self.users.append(user)
        return user

    def update(self, id: int, input: User):
        for i, user in enumerate(self.users):
            if user.id == id:
                input.id = id
                self.users[i] = input

    def delete(self, id: int,):
        for i, user in enumerate(self.users):
            if user.id == id:
                del self.users[i]

    # конец решения
