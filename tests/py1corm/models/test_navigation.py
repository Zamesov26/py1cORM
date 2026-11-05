from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field, Mapped, Navigation
from py1cORM.odata.query import QuerySet


class Row(ODataModel):
    name: Mapped[str] = Field(alias='Description')


class Document(ODataModel):
    rows: Mapped[list[Row]] = Navigation(model=Row, alias='Rows')

    class Meta:
        entity_name = 'Documents'


def test_returns_related_model_when_navigation_is_configured():
    field = Document._fields['rows']

    assert field.get_related_model() is Row


def test_builds_nested_path_when_navigation_field_is_traversed():
    query = QuerySet(None, Document).select(Document.rows.then(Row.name))

    assert query.spec.select == ['Rows/Description']


def test_builds_expand_path_when_navigation_field_is_selected():
    query = QuerySet(None, Document).expand(Document.rows)

    assert query.spec.expand == ['Rows']
