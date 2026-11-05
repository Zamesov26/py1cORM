from uuid import UUID

import pytest

from py1cORM.exceptions import FieldNotLoadedError
from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field, Mapped, Relationship


class WorkCenterModel(ODataModel):
    uid: Mapped[str] = Field(alias='ВидРабочегоЦентра_Key')


class ProductStageModel(ODataModel):
    owner_id: Mapped[str] = Field(alias='Owner_Key')
    work_centers: Mapped[list[WorkCenterModel]] = Field(alias='ВидыРабочихЦентров')


class ResourceSpecificationsModel(ODataModel):
    product_stage_id: Mapped[UUID | None] = Field(alias='ОсновноеИзделиеЭтап_Key')
    product_stage: Mapped[ProductStageModel | None] = Relationship(
        model=ProductStageModel,
        alias='ОсновноеИзделиеЭтап',
    )


def test_contains_key_only_when_relation_is_not_expanded():
    raw = {'ОсновноеИзделиеЭтап_Key': '550e8400-e29b-41d4-a716-446655440000'}

    entity = ResourceSpecificationsModel.from_raw(raw)

    assert entity.product_stage_id == UUID('550e8400-e29b-41d4-a716-446655440000')
    assert not entity.is_loaded('product_stage')


def test_contains_entity_when_relation_is_expanded():
    raw = {
        'ОсновноеИзделиеЭтап_Key': '550e8400-e29b-41d4-a716-446655440000',
        'ОсновноеИзделиеЭтап': {
            'Ref_Key': '550e8400-e29b-41d4-a716-446655440000',
            'Description': 'Stage',
        },
    }

    entity = ResourceSpecificationsModel.from_raw(raw)

    assert entity.product_stage_id == UUID('550e8400-e29b-41d4-a716-446655440000')
    assert entity.product_stage is not None


def test_marks_relation_not_loaded_when_key_and_entity_are_absent():
    raw = {}

    entity = ResourceSpecificationsModel.from_raw(raw)

    assert not entity.is_loaded('product_stage')

    with pytest.raises(FieldNotLoadedError):
        _ = entity.product_stage
