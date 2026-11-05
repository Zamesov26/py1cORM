import pytest

from py1cORM.exceptions import FieldNotLoadedError
from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field, Mapped


class WorkCenterModel(ODataModel):
    uid: Mapped[str] = Field(alias='ВидРабочегоЦентра_Key')
    name: Mapped[str] = Field(alias='Description')


class ProductStageModel(ODataModel):
    owner_id: Mapped[str] = Field(alias='Owner_Key')
    work_centers: Mapped[list[WorkCenterModel]] = Field(alias='ВидыРабочихЦентров')


def test_builds_entity_when_embedded_value_is_object():

    raw = {
        'Owner_Key': '550e8400-e29b-41d4-a716-446655440000',
        'ВидыРабочихЦентров': [],
    }

    entity = ProductStageModel.from_raw(raw)

    assert entity.owner_id is not None
    assert entity.work_centers == []


def test_builds_entities_when_embedded_value_is_list():

    raw = {
        'Owner_Key': '550e8400-e29b-41d4-a716-446655440000',
        'ВидыРабочихЦентров': [
            {
                'ВидРабочегоЦентра_Key': '11111111-1111-1111-1111-111111111111',
                'Description': 'description_1',
            },
            {
                'ВидРабочегоЦентра_Key': '22222222-2222-2222-2222-222222222222',
                'Description': 'description_2',
            },
        ],
    }

    entity = ProductStageModel.from_raw(raw)

    assert len(entity.work_centers) == 2
    assert entity.work_centers[0].uid is not None
    assert entity.work_centers[0].name == 'description_1'


def test_marks_nested_field_not_loaded_when_value_is_absent():

    raw = {'Owner_Key': '550e8400-e29b-41d4-a716-446655440000'}

    entity = ProductStageModel.from_raw(raw)

    assert entity.is_loaded('work_centers') is False

    with pytest.raises(FieldNotLoadedError):
        _ = entity.work_centers


def test_preserves_extra_fields_when_nested_value_contains_unknown_data():

    raw = {
        'Owner_Key': '550e8400-e29b-41d4-a716-446655440000',
        'ВидыРабочихЦентров': [{'ВидРабочегоЦентра_Key': '111', 'Unexpected': 123}],
    }

    entity = ProductStageModel.from_raw(raw)

    wc = entity.work_centers[0]

    assert wc.extra() == {'Unexpected': 123}
