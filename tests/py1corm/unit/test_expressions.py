from uuid import UUID

from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field


class TestModel(ODataModel):
    uid: UUID = Field(
        alias='Ref_Key',
        entity_type='Document_ЗаказКлиента',
    )


def test_uuid_field_with_entity_type_uses_cast():
    expr = (
        TestModel.uid
        == UUID('8600cb3a-3f1a-11f1-aa9b-ac1f6bd30991')
    )

    assert expr.to_odata() == (
        "Ref_Key eq "
        "cast(guid'8600cb3a-3f1a-11f1-aa9b-ac1f6bd30991', "
        "'Document_ЗаказКлиента')"
    )
    


def test_uuid_field_without_entity_type():
    class TestModel(ODataModel):
        uid: UUID = Field(alias='Ref_Key')
    
    expr = (
        TestModel.uid
        == UUID('8600cb3a-3f1a-11f1-aa9b-ac1f6bd30991')
    )

    assert expr.to_odata() == (
        "Ref_Key eq "
        "guid'8600cb3a-3f1a-11f1-aa9b-ac1f6bd30991'"
    )