import pytest

from py1cORM.exceptions import FieldNotLoadedError
from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Embedded, Field


class Nomenclature(ODataModel):
    ref_key: str = Field(alias='Ref_Key')
    name: str = Field(alias='Description')


class Product(ODataModel):
    nomenclature: Nomenclature | None = Embedded(
        model=Nomenclature,
        alias='Номенклатура',
        expand_only=True,
    )


RAW = {}


def test_expand_only_not_loaded():

    entity = Product.from_raw(RAW)

    with pytest.raises(FieldNotLoadedError):
        _ = entity.nomenclature


def test_expand_only_loaded():

    raw = {'Номенклатура': {'Ref_Key': '123', 'Description': 'Test product'}}

    entity = Product.from_raw(raw)

    assert entity.nomenclature.name == 'Test product'


def test_expand_only_null():

    raw = {'Номенклатура': None}

    entity = Product.from_raw(raw)

    assert entity.nomenclature is None
