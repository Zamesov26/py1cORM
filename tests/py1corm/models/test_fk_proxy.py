import pytest

from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field, ForeignKey
from py1cORM.models.relations import FK


class RelatedModel(ODataModel):
    value: int = Field(alias='value')

    class Meta:
        entity_name = 'Related'


class SomeModel(ODataModel):
    ref: str = Field(alias='Ref_Key')

    related = ForeignKey(
        model=RelatedModel,
        key_field='Related_Key',
        alias='Related',
    )

    class Meta:
        entity_name = 'Some'


class Dummy:
    def __init__(self):
        self.value = 42
        self.items = [1, 2, 3]

    def __iter__(self):
        return iter(self.items)


def test_proxies_attribute_when_related_entity_is_loaded():
    entity = Dummy()
    fk = FK(key=1, entity=entity)

    assert fk.value == 42


def test_rejects_attribute_access_when_related_entity_is_not_loaded():
    fk = FK(key=1, entity=None)

    with pytest.raises(AttributeError):
        _ = fk.value


def test_proxies_related_attribute_when_entity_contains_foreign_key():
    raw = {'Ref_Key': '123', 'Related': {'value': 10}}

    obj = SomeModel.from_raw(raw)

    assert obj.related.value == 10
