from uuid import UUID

from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field, Mapped
from py1cORM.odata.fields import like
from py1cORM.odata.query import QuerySet


class NomenclatureModel(ODataModel):
    uid: Mapped[UUID] = Field(alias='Ref_Key')
    name: Mapped[str] = Field(alias='Description')

    class Meta:
        entity_name = 'Catalog_Номенклатура'


def test_builds_like_filter_when_pattern_is_given():
    expr = like(NomenclatureModel.name, 'Стакан%')

    qs = QuerySet(client=None, model=NomenclatureModel).filter(expr)

    assert qs.spec.filter == "like(Description, 'Стакан%')"
