import pytest
from src.core.exceptions import ConflictError, DomainValidationError
from src.models import CI, CIType, Relation
from src.schemas.ci import CITypeCreate, CITypeUpdate


@pytest.mark.asyncio
async def test_delete_type_blocked_by_active_ci(db_session, admin_user, ci_type_write_service, async_bundle):
    user = admin_user
    type_name = "Delete Block Test Type"
    created = await ci_type_write_service.create_type(
        CITypeCreate(name=type_name, description="test", attribute_schema={"properties": {}}),
        user,
    )
    await async_bundle.session.commit()
    db_session.add(
        CI(
            name="blocks-type-delete",
            type_id=created["id"],
            status="active",
            owner="qa",
            environment="test",
            criticality="low",
        )
    )
    db_session.commit()

    with pytest.raises(ConflictError, match="active CI"):
        await ci_type_write_service.delete_type(created["id"], user)


@pytest.mark.asyncio
async def test_delete_type_purges_recycled_cis(
    db_session, admin_user, ci_type_write_service, ci_write_service, async_bundle
):
    user = admin_user
    type_name = "Delete Recycle Purge Type"
    created = await ci_type_write_service.create_type(
        CITypeCreate(name=type_name, description="test", attribute_schema={"properties": {}}),
        user,
    )
    await async_bundle.session.commit()
    ci = CI(
        name="recycled-for-type-delete",
        type_id=created["id"],
        status="active",
        owner="qa",
        environment="test",
        criticality="low",
    )
    db_session.add(ci)
    db_session.commit()
    await ci_write_service.delete_ci(ci.id, user)
    await async_bundle.session.commit()

    result = await ci_type_write_service.delete_type(created["id"], user)
    await async_bundle.session.commit()
    assert result == {"ok": True}
    assert db_session.query(CIType).filter(CIType.id == created["id"]).first() is None
    assert db_session.query(CI).filter(CI.id == ci.id).first() is None


@pytest.mark.asyncio
async def test_delete_type_purges_recycled_cis_with_relations(
    db_session, admin_user, ci_type_write_service, ci_write_service, async_bundle
):
    user = admin_user
    server_type = db_session.query(CIType).filter(CIType.name == "Server").first()
    created = await ci_type_write_service.create_type(
        CITypeCreate(name="Delete With Relations Type", description="test", attribute_schema={"properties": {}}),
        user,
    )
    await async_bundle.session.commit()
    anchor = CI(
        name="anchor-for-rel",
        type_id=server_type.id,
        status="active",
        owner="qa",
        environment="test",
        criticality="low",
    )
    target = CI(
        name="recycled-with-rel",
        type_id=created["id"],
        status="active",
        owner="qa",
        environment="test",
        criticality="low",
    )
    db_session.add_all([anchor, target])
    db_session.commit()
    db_session.add(
        Relation(source_ci_id=anchor.id, target_ci_id=target.id, relation_type="depends_on", status="active")
    )
    db_session.commit()
    await ci_write_service.delete_ci(target.id, user)
    await async_bundle.session.commit()

    result = await ci_type_write_service.delete_type(created["id"], user)
    await async_bundle.session.commit()
    assert result == {"ok": True}
    assert db_session.query(Relation).filter(Relation.target_ci_id == target.id).count() == 0


@pytest.mark.asyncio
async def test_update_type_name_conflict(db_session, admin_user, ci_type_write_service, async_bundle):
    a = await ci_type_write_service.create_type(
        CITypeCreate(name="UniqueTypeA", description="", attribute_schema={"properties": {}}),
        admin_user,
    )
    await ci_type_write_service.create_type(
        CITypeCreate(name="UniqueTypeB", description="", attribute_schema={"properties": {}}),
        admin_user,
    )
    await async_bundle.session.commit()
    with pytest.raises(ConflictError, match="already exists"):
        await ci_type_write_service.update_type(a["id"], CITypeUpdate(name="UniqueTypeB"), admin_user)


@pytest.mark.asyncio
async def test_delete_official_type_rejected(db_session, admin_user, ci_type_write_service):
    server_type = db_session.query(CIType).filter(CIType.name == "Server").first()
    with pytest.raises(DomainValidationError, match="official"):
        await ci_type_write_service.delete_type(server_type.id, admin_user)


@pytest.mark.asyncio
async def test_create_type_name_conflict(db_session, admin_user, ci_type_write_service, async_bundle):
    await ci_type_write_service.create_type(
        CITypeCreate(name="DupTypeName", description="", attribute_schema={"properties": {}}),
        admin_user,
    )
    await async_bundle.session.commit()
    with pytest.raises(ConflictError, match="already exists"):
        await ci_type_write_service.create_type(
            CITypeCreate(name="DupTypeName", description="", attribute_schema={"properties": {}}),
            admin_user,
        )
