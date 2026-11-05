from uuid import UUID

from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field


class TestModel(ODataModel):
    uid: UUID | None = Field(alias='Ref_Key')
    name: str = Field(alias='Description')


def test_collects_fields_when_model_class_is_created():
    assert 'uid' in TestModel._fields
    assert 'name' in TestModel._fields


def test_builds_alias_map_when_model_class_is_created():
    assert TestModel._alias_map['Ref_Key'] == 'uid'
    assert TestModel._alias_map['Description'] == 'name'


def test_stores_annotation_when_field_is_bound():
    field = TestModel._fields['uid']
    assert field.annotation == UUID | None
