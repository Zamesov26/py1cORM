from uuid import UUID

import pytest

from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field, Mapped
from py1cORM.odata.fields import FieldRef
from py1cORM.odata.query import QuerySet


class TestModel(ODataModel):
    uid: Mapped[UUID | None] = Field(alias='Ref_Key')
    name: Mapped[str] = Field(alias='Description')


def test_collects_fields_when_model_class_is_created():
    assert 'uid' in TestModel._fields
    assert 'name' in TestModel._fields


def test_builds_alias_map_when_model_class_is_created():
    assert TestModel._alias_map['Ref_Key'] == 'uid'
    assert TestModel._alias_map['Description'] == 'name'


def test_stores_annotation_when_field_is_bound():
    field = TestModel._fields['uid']
    assert field.annotation == UUID | None


def test_returns_model_instance_when_raw_data_is_parsed():
    entity = TestModel.from_raw({'Ref_Key': str(UUID(int=1)), 'Description': 'Cup'})

    assert isinstance(entity, TestModel)
    assert entity.name == 'Cup'
    assert isinstance(TestModel.name, FieldRef)


def test_rejects_field_without_mapped_annotation():
    with pytest.raises(TypeError, match=r'must be annotated as Mapped\[T\]'):

        class LegacyModel(ODataModel):
            uid: UUID = Field(alias='Ref_Key')


def test_creates_typed_queryset_for_model_connection():
    connection = object()

    query = TestModel.using(connection)

    assert isinstance(query, QuerySet)
    assert query.client is connection
    assert query.model is TestModel
