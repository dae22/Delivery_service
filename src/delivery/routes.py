import uuid

from fastapi import APIRouter, Cookie, Depends, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from delivery.database import get_db
from delivery.models import PackageTypeDB
from delivery.schemas import CreatePackage, CreatePackageReply, Pagination, ShowPackageReply, ShowPackagesType
from delivery.services import PackageService

router = APIRouter(prefix="/packages", tags=["Packages"])


@router.post("/", response_model=CreatePackageReply, summary="Зарегистрировать посылку")
async def create_package(
    package: CreatePackage, response: Response, session_id: str = Cookie(None), service: PackageService = Depends()
):
    if session_id is None:
        session_id = str(uuid.uuid4())
        response.set_cookie(key="session_id", value=session_id, httponly=True)

    new_package_id = await service.create(package=package, session_id=session_id)
    return {"id": new_package_id}


@router.get("/types", response_model=list[ShowPackagesType], summary="Получить все типы посылок")
async def show_packages_type(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PackageTypeDB))
    types = result.scalars().all()
    return types


@router.get("/my_packages", response_model=list[ShowPackageReply], summary="Получить список посылок пользователя")
async def show_user_packages(
    pagination: Pagination = Depends(),
    response: Response = None,
    session_id: str = Cookie(None),
    service: PackageService = Depends(),
):
    if session_id is None:
        session_id = str(uuid.uuid4())
        response.set_cookie(key="session_id", value=session_id, httponly=True)

    packages = await service.get_packages(session_id=session_id, pagination=pagination)
    return packages


@router.get("/{package_id}", response_model=ShowPackageReply, summary="Получить посылку по id")
async def show_package(
    package_id: int, response: Response = None, session_id: str = Cookie(None), service: PackageService = Depends()
):
    if session_id is None:
        session_id = str(uuid.uuid4())
        response.set_cookie(key="session_id", value=session_id, httponly=True)

    return await service.get_by_id(package_id=package_id, session_id=session_id)
