from sqlalchemy import ForeignKey, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True


class PackageTypeDB(Base):
    __tablename__ = "package_type"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)

    packages: Mapped[list["PackagesDB"]] = relationship(back_populates="package_type")


class PackagesDB(Base):
    __tablename__ = "packages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    weight: Mapped[float]
    type_id: Mapped[int] = mapped_column(ForeignKey("package_type.id"))
    price: Mapped[float]
    session_id: Mapped[str] = mapped_column(index=True)
    delivery_price: Mapped[float | None] = mapped_column(nullable=True)

    package_type: Mapped["PackageTypeDB"] = relationship(back_populates="packages")


async def init_package_type(db):
    from sqlalchemy import select

    result = await db.execute(select(PackageTypeDB))
    existing_types = result.scalars().all()

    if not existing_types:
        default_types = [PackageTypeDB(name="Одежда"), PackageTypeDB(name="Электроника"), PackageTypeDB(name="Разное")]
        db.add_all(default_types)
        await db.commit()
