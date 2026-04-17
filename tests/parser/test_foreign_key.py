import pytest

from py1cORM.exceptions import FieldNotLoadedError
from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field, ForeignKey


class WorkCenterModel(ODataModel):
    uid: str = Field(alias='ВидРабочегоЦентра_Key')


class ProductStageModel(ODataModel):
    owner_id: str = Field(alias='Owner_Key')
    work_centers: list[WorkCenterModel] = Field(alias='ВидыРабочихЦентров')


class ResourceSpecificationsModel(ODataModel):
    product_stage: ProductStageModel | None = ForeignKey(
        model=ProductStageModel,
        alias='ОсновноеИзделиеЭтап',
        key_field='ОсновноеИзделиеЭтап_Key',
    )


def test_fk_only_key():
    raw = {'ОсновноеИзделиеЭтап_Key': '550e8400-e29b-41d4-a716-446655440000'}

    entity = ResourceSpecificationsModel.from_raw(raw)

    assert entity.product_stage._id is not None
    assert entity.product_stage._entity is None


def test_fk_with_expand():
    raw = {
        'ОсновноеИзделиеЭтап_Key': '550e8400-e29b-41d4-a716-446655440000',
        'ОсновноеИзделиеЭтап': {
            'Ref_Key': '550e8400-e29b-41d4-a716-446655440000',
            'Description': 'Stage',
        },
    }

    entity = ResourceSpecificationsModel.from_raw(raw)

    assert entity.product_stage._id is not None
    assert entity.product_stage._entity is not None


def test_fk_not_loaded():
    raw = {}

    entity = ResourceSpecificationsModel.from_raw(raw)

    assert not entity.is_loaded('product_stage')

    with pytest.raises(FieldNotLoadedError):
        _ = entity.product_stage
