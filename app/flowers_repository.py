from attrs import define


@define
class Flower:
    name: str
    count: int
    cost: int
    id: int = 0


class FlowersRepository:
    flowers: list[Flower]

    def __init__(self):
        self.flowers = []

    # необходимые методы сюда
    def get_all(self):
        return self.flowers

    def get_one(self, id):
        for flower in self.flowers:
            if id == flower.id:
                return flower
        return None

    def save(self, flower: Flower):
        flower.id = len(self.flowers) + 1
        self.flowers.append(flower)
        return flower

    def update(self, id: int, input: Flower):
        for i, flower in enumerate(self.flowers):
            if flower.id == id:
                input.id = id
                self.flowers[i] = input

    def delete(
        self,
        id: int,
    ):
        for i, flower in enumerate(self.flowers):
            if flower.id == id:
                del self.flowers[i]

    # конец решения
