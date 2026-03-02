import pytest

from py1cORM.exceptions import FieldNotLoadedError
from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field
from py1cORM.parser.sentinels import NotLoaded


class TestModel(ODataModel):
    uid: str = Field(alias='Ref_Key')
    name: str = Field(alias='Description')


def test_entity_sets_loaded_fields():
    raw = {'Ref_Key': '123'}

    entity = TestModel.from_raw(raw)

    assert entity.uid == '123'
    assert entity.__dict__['name'] is NotLoaded
    assert entity.is_loaded('uid') is True
    assert entity.is_loaded('name') is False


def test_extra_fields_collected():
    raw = {
        'Ref_Key': '123',
        'Unexpected': 42,
    }

    entity = TestModel.from_raw(raw)

    assert entity._extra == {'Unexpected': 42}


def test_access_not_loaded_field_raises():
    raw = {'Ref_Key': '123'}

    entity = TestModel.from_raw(raw)

    with pytest.raises(FieldNotLoadedError) as exc:
        _ = entity.name

    assert "Field 'name' was not loaded" in str(exc.value)
