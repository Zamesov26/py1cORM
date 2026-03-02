from uuid import UUID

from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field


class TestModel(ODataModel):
    uid: UUID | None = Field(alias='Ref_Key')
    name: str = Field(alias='Description')


def test_fields_collected():
    assert 'uid' in TestModel._fields
    assert 'name' in TestModel._fields


def test_alias_map():
    assert TestModel._alias_map['Ref_Key'] == 'uid'
    assert TestModel._alias_map['Description'] == 'name'


def test_annotation_stored():
    field = TestModel._fields['uid']
    assert field.annotation == UUID | None
