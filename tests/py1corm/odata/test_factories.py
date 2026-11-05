from tests.models import Category

from py1cORM.models.fields import Embedded as EmbeddedField
from py1cORM.models.fields import Field as ScalarField
from py1cORM.models.fields import Relationship as RelationshipField
from py1cORM.odata.factories import Embedded, Field, Relationship


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


def test_enables_auto_expand_when_relationship_factory_is_called():
    field = Relationship(
        model=Category,
        alias='Category',
    )

    assert isinstance(field, RelationshipField)
    assert field.related_model is Category
    assert field.auto_expand is True
