from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field, Mapped, Relationship


class RelatedModel(ODataModel):
    value: Mapped[int] = Field(alias='value')

    class Meta:
        entity_name = 'Related'


class SomeModel(ODataModel):
    ref: Mapped[str] = Field(alias='Ref_Key')

    related: Mapped[RelatedModel | None] = Relationship(
        model=RelatedModel,
        alias='Related',
    )

    class Meta:
        entity_name = 'Some'


def test_exposes_related_entity_when_foreign_key_is_expanded():
    raw = {'Ref_Key': '123', 'Related': {'value': 10}}

    obj = SomeModel.from_raw(raw)

    assert obj.related is not None
    assert obj.related.value == 10
