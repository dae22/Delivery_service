from typing import Optional, Union

from fastapi import Query
from pydantic import BaseModel, field_validator


class CreatePackage(BaseModel):
    name: str
    weight: float
    type_id: int
    price: float

    @field_validator("price", "weight")
    def validate(cls, value):
        if not value > 0:
            raise ValueError("Value must be positive")
        return value


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
