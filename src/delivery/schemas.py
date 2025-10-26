from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator


def to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class CreatePackage(BaseModel):
    name: str
    weight: Annotated[float, Field(..., ge=1)]  # Эта запись заменяет @field_validator
    type_id: Annotated[int, Field(..., alias="typeId")]  # Также псевдоним можно назначить так в ручную
    price: Annotated[float, Field(..., ge=1)]

    @field_validator("price", "weight")
    def validate(cls, value):
        if not value > 0:
            raise ValueError("Value must be positive")
        return value

    @field_serializer("name")
    def serialize_name(self, value: str):
        return value.capitalize()

    model_config = ConfigDict(
        alias_generator=to_camel,  # Делает псевдонимы поля
        populate_by_name=True,  # Разрешает обращение по псевдониму
    )


class CreatePackageReply(BaseModel):
    id: int


class Pagination(BaseModel):
    type_id: int | None = Query(None)
    has_delivery_price: bool | None = Query(None)
    page: int = Query(1, ge=1)
    limit: int = Query(10, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class ShowPackageReply(BaseModel):
    id: int
    name: str
    weight: float
    price: float
    delivery_price: float | str
    type_name: str


class ShowPackagesType(BaseModel):
    id: int
    name: str
