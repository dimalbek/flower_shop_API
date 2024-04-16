from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .models import Flower
from attrs import define
from pydantic import BaseModel
from typing import List


class FlowerRequest(BaseModel):
    name: str
    count: int | None = None
    cost: float


class PatchFlowerRequest(BaseModel):
    name: str | None = None
    count: int | None = None
    cost: float | None = None


class FlowerResponse(BaseModel):
    id: int
    name: str
    count: int
    cost: float


class FlowersRepository:
    flowers: list[Flower]

    def save_flower(self, db: Session, flower: FlowerRequest) -> int:
        db_flower = Flower(name=flower.name, count=flower.count, cost=flower.cost)
        try:
            db.add(db_flower)
            db.commit()
            db.refresh(db_flower)

        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Invalid flower data")

        return db_flower.id

    def get_all(self, db: Session, skip: int = 0, limit: int = 10) -> List[Flower]:
        return db.query(Flower).offset(skip).limit(limit).all()

    def update_flower(
        self, db: Session, flower_id: int, flower_data: PatchFlowerRequest
    ) -> Flower:
        db_flower = db.query(Flower).filter(Flower.id == flower_id).first()
        if db_flower is None:
            raise HTTPException(status_code=404, detail="Flower not found")

        updates = flower_data.dict(exclude_unset=True)
        if not updates:
            raise HTTPException(status_code=400, detail="No data provided to update")

        for key, value in updates.items():
            setattr(db_flower, key, value)
        try:
            db.commit()
            db.refresh(db_flower)
            return db_flower
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Invalid flower data")

    def delete_flower(self, db: Session, flower_id: int):
        db_flower = db.query(Flower).filter(Flower.id == flower_id).first()
        if db_flower is None:
            raise HTTPException(status_code=404, detail="Flower not found")
        db.delete(db_flower)
        db.commit()
        return db_flower
        return {"message": f"Flower with id {flower_id} deleted"}
