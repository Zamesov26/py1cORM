from uuid import UUID

import pytest

from py1cORM.exceptions import FieldNotLoadedError
from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field, ForeignKey

# ---------------------------
# Тестовые модели
# ---------------------------


class WorkCenterModel(ODataModel):
    uid: UUID | None = Field(alias='ВидРабочегоЦентра_Key')
    name: str = Field(alias='Description')


class ProductStageModel(ODataModel):
    owner_id: UUID | None = Field(alias='Owner_Key')
    work_centers: list[WorkCenterModel] = Field(alias='ВидыРабочихЦентров')


class ResourceSpecificationsModel(ODataModel):
    name: str = Field(alias='Description')

    product_stage: ProductStageModel | None = ForeignKey(
        model=ProductStageModel,
        alias='ОсновноеИзделиеЭтап',
        key_field='ОсновноеИзделиеЭтап_Key',
    )


# ---------------------------
# Интеграционный тест
# ---------------------------


def test_full_graph_parsing():

    raw = {
        'Description': 'Specification A',
        'ОсновноеИзделиеЭтап_Key': '550e8400-e29b-41d4-a716-446655440000',
        'ОсновноеИзделиеЭтап': {
            'Owner_Key': '11111111-1111-1111-1111-111111111111',
            'ВидыРабочихЦентров': [
                {
                    'ВидРабочегоЦентра_Key': '22222222-2222-2222-2222-222222222222',
                    'Description': 'WC-1',
                    'UnexpectedField': 'extra',
                },
                {
                    'ВидРабочегоЦентра_Key': '00000000-0000-0000-0000-000000000000',
                    'Description': 'WC-2',
                },
            ],
        },
        'ExtraRootField': 123,
    }

    entity = ResourceSpecificationsModel.from_raw(raw)

    # --- root scalar
    assert entity.name == 'Specification A'

    # --- extra root
    assert entity.extra() == {'ExtraRootField': 123}

    # --- FK key
    assert entity.product_stage._id == UUID('550e8400-e29b-41d4-a716-446655440000')

    # --- FK expand
    stage = entity.product_stage._entity
    assert stage.owner_id == UUID('11111111-1111-1111-1111-111111111111')

    # --- nested list
    assert len(stage.work_centers) == 2

    wc1 = stage.work_centers[0]
    assert wc1.uid == UUID('22222222-2222-2222-2222-222222222222')
    assert wc1.name == 'WC-1'
    assert wc1.extra() == {'UnexpectedField': 'extra'}

    # --- ZERO UUID → None
    wc2 = stage.work_centers[1]
    assert wc2.uid is None

    # --- NotLoaded проверка
    raw_no_stage = {'Description': 'No expand'}

    entity2 = ResourceSpecificationsModel.from_raw(raw_no_stage)

    assert not entity2.is_loaded('product_stage')

    with pytest.raises(FieldNotLoadedError):
        _ = entity2.product_stage
