import pytest

from py1cORM.exceptions import FieldNotLoadedError
from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field


class WorkCenterModel(ODataModel):
    uid: str = Field(alias='ВидРабочегоЦентра_Key')
    name: str = Field(alias='Description')


class ProductStageModel(ODataModel):
    owner_id: str = Field(alias='Owner_Key')
    work_centers: list[WorkCenterModel] = Field(alias='ВидыРабочихЦентров')


def test_embedded_single_object():

    raw = {
        'Owner_Key': '550e8400-e29b-41d4-a716-446655440000',
        'ВидыРабочихЦентров': [],
    }

    entity = ProductStageModel.from_raw(raw)

    assert entity.owner_id is not None
    assert entity.work_centers == []


def test_embedded_list():

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


def test_nested_not_loaded():

    raw = {'Owner_Key': '550e8400-e29b-41d4-a716-446655440000'}

    entity = ProductStageModel.from_raw(raw)

    assert entity.is_loaded('work_centers') is False

    with pytest.raises(FieldNotLoadedError):
        _ = entity.work_centers


def test_nested_extra_fields():

    raw = {
        'Owner_Key': '550e8400-e29b-41d4-a716-446655440000',
        'ВидыРабочихЦентров': [{'ВидРабочегоЦентра_Key': '111', 'Unexpected': 123}],
    }

    entity = ProductStageModel.from_raw(raw)

    wc = entity.work_centers[0]

    assert wc.extra() == {'Unexpected': 123}
