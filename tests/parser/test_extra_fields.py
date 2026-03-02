from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field


class TestModel(ODataModel):
    uid: str = Field(alias='Ref_Key')


def test_extra_fields_collected():
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
