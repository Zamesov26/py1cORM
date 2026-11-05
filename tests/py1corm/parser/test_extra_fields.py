from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field


class TestModel(ODataModel):
    uid: str = Field(alias='Ref_Key')


def test_collects_unknown_values_when_parsing_entity():
    raw = {
        'Ref_Key': '123',
        'Unknown': 'X',
        'Another': 5,
    }

    entity = TestModel.from_raw(raw)

    assert entity.uid == '123'
    assert entity.extra() == {
        'Unknown': 'X',
        'Another': 5,
    }
