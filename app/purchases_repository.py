from attrs import define


@define
class Purchase:
    user_id: int = 0
    flower_id: int = 0


class PurchasesRepository:
    purchases: list[Purchase]

    def __init__(self):
        self.purchases = []

    # необходимые методы сюда

    # конец решения
