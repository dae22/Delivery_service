from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from delivery.database import get_db
from delivery.models import PackagesDB
from delivery.schemas import ShowPackageReply


class PackageService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def create(self, package, session_id):
        new_package = PackagesDB(
            name=package.name,
            weight=package.weight,
            type_id=package.type_id,
            price=package.price,
            session_id=session_id,
        )
        self.db.add(new_package)
        await self.db.commit()
        await self.db.refresh(new_package)
        return new_package.id

    async def get_packages(self, session_id, pagination):
        stmt = select(PackagesDB).where(PackagesDB.session_id == session_id)

        if pagination.type_id is not None:
            stmt = stmt.where(PackagesDB.type_id == pagination.type_id)

        if pagination.has_delivery_price is not None:
            if pagination.has_delivery_price:
                stmt = stmt.where(PackagesDB.delivery_price.isnot(None))
            else:
                stmt = stmt.where(PackagesDB.delivery_price.is_(None))

        stmt = stmt.offset(pagination.offset).limit(pagination.limit)

        result = await self.db.execute(stmt)
        packages = result.scalars().all()

        for pkg in packages:
            await self.db.refresh(pkg, attribute_names=["package_type"])

        return [
            ShowPackageReply(
                id=pkg.id,
                name=pkg.name,
                weight=pkg.weight,
                price=pkg.price,
                delivery_price=pkg.delivery_price if pkg.delivery_price is not None else "Не рассчитано",
                type_name=pkg.package_type.name if pkg.package_type else None,
            )
            for pkg in packages
        ]

    async def get_by_id(self, package_id, session_id):
        stmt = (
            select(PackagesDB)
            .options(joinedload(PackagesDB.package_type))
            .where(PackagesDB.session_id == session_id, PackagesDB.id == package_id)
        )
        result = await self.db.execute(stmt)
        package = result.scalar_one_or_none()

        if not package:
            raise HTTPException(status_code=404, detail="Посылка не найдена")

        return ShowPackageReply(
            id=package.id,
            name=package.name,
            weight=package.weight,
            price=package.price,
            delivery_price=package.delivery_price if package.delivery_price is not None else "Не рассчитано",
            type_name=package.package_type.name,
        )
