from uuid import UUID

from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field, Mapped


class TestModel(ODataModel):
    uid: Mapped[UUID] = Field(
        alias='Ref_Key',
        entity_type='Document_ЗаказКлиента',
    )


def test_uses_cast_when_uuid_field_has_entity_type():
    expr = TestModel.uid == UUID('8600cb3a-3f1a-11f1-aa9b-ac1f6bd30991')

    assert expr.to_odata() == (
        'Ref_Key eq '
        "cast(guid'8600cb3a-3f1a-11f1-aa9b-ac1f6bd30991', "
        "'Document_ЗаказКлиента')"
    )


def test_uses_guid_literal_when_uuid_field_has_no_entity_type():
    class TestModel(ODataModel):
        uid: Mapped[UUID] = Field(alias='Ref_Key')

    expr = TestModel.uid == UUID('8600cb3a-3f1a-11f1-aa9b-ac1f6bd30991')

    assert expr.to_odata() == ("Ref_Key eq guid'8600cb3a-3f1a-11f1-aa9b-ac1f6bd30991'")
