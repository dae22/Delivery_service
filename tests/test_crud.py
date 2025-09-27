import pytest
from sqlalchemy import select

from delivery.models import PackagesDB, PackageTypeDB, init_package_type


@pytest.mark.asyncio
async def test_create_packages_type(client, db_session):
    await init_package_type(db_session)
    result = await db_session.execute(select(PackageTypeDB))
    packages_type = result.scalars().all()
    assert len(packages_type) == 3


@pytest.mark.asyncio
async def test_create_package(client, db_session):
    data = {"name": "jacket", "weight": 2, "type_id": 1, "price": 10}
    result = await client.post("/packages", json=data)
    assert result.status_code == 200

    query = await db_session.execute(select(PackagesDB).where(PackagesDB.name == data["name"]))
    pkg = query.scalar_one_or_none()
    assert pkg is not None
    assert pkg.weight == data["weight"]
