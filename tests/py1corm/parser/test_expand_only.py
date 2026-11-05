import pytest

from py1cORM.exceptions import FieldNotLoadedError
from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Embedded, Field, Mapped


class Nomenclature(ODataModel):
    ref_key: Mapped[str] = Field(alias='Ref_Key')
    name: Mapped[str] = Field(alias='Description')


class Product(ODataModel):
    nomenclature: Mapped[Nomenclature | None] = Embedded(
        model=Nomenclature,
        alias='Номенклатура',
        expand_only=True,
    )


RAW = {}


def test_marks_field_not_loaded_when_expand_only_value_is_absent():

    entity = Product.from_raw(RAW)

    with pytest.raises(FieldNotLoadedError):
        _ = entity.nomenclature


def test_loads_field_when_expand_only_value_is_present():

    raw = {'Номенклатура': {'Ref_Key': '123', 'Description': 'Test product'}}

    entity = Product.from_raw(raw)

    assert entity.nomenclature.name == 'Test product'


def test_loads_none_when_expand_only_value_is_null():

    raw = {'Номенклатура': None}

    entity = Product.from_raw(raw)

    assert entity.nomenclature is None
