from tests.models import Category

from py1cORM.models.fields import Embedded as EmbeddedField
from py1cORM.models.fields import Field as ScalarField
from py1cORM.models.fields import ForeignKey as ForeignKeyField
from py1cORM.odata.factories import Embedded, Field, ForeignKey


def test_returns_scalar_field_when_field_factory_is_called():
    field = Field(alias='Description', default='')

    assert isinstance(field, ScalarField)
    assert field.alias == 'Description'
    assert field.default == ''


def test_returns_embedded_field_when_embedded_factory_is_called():
    field = Embedded(model=Category, alias='Categories')

    assert isinstance(field, EmbeddedField)
    assert field.embedded_model is Category
    assert field.alias == 'Categories'


def test_enables_auto_expand_when_foreign_key_factory_is_called():
    field = ForeignKey(
        model=Category,
        key_field='Category_Key',
        alias='Category',
    )

    assert isinstance(field, ForeignKeyField)
    assert field.related_model is Category
    assert field.key_field == 'Category_Key'
    assert field.auto_expand is True
