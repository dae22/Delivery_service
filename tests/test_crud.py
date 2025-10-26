import pytest
from sqlalchemy import delete, select

from delivery.models import Base, PackagesDB, PackageTypeDB, init_package_type


@pytest.mark.asyncio
async def test_create_packages_type(db_session):
    await init_package_type(db_session)
    result = await db_session.execute(select(PackageTypeDB))
    packages_type = result.scalars().all()
    assert len(packages_type) == 3


@pytest.mark.asyncio
async def test_create_package(test_client, db_session):
    data = {"name": "jacket", "weight": 2, "type_id": 1, "price": 10}
    result = await test_client.post("/packages/", json=data)

    assert result.status_code == 200

    response_data = result.json()
    new_package_id = response_data["id"]
    query = await db_session.execute(select(PackagesDB).where(PackagesDB.id == new_package_id))
    pkg = query.scalar_one_or_none()

    assert pkg is not None
    assert pkg.weight == data["weight"]


@pytest.mark.asyncio
async def test_delete_tables(db_session):
    for table in reversed(Base.metadata.sorted_tables):
        await db_session.execute(delete(table))
    await db_session.commit()
