from uuid import UUID

from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field

# --------------------------------
# Тестовая модель
# --------------------------------

class TestModel(ODataModel):
    uid: UUID = Field(alias="Ref_Key")
    name: str = Field(alias="Description")


# --------------------------------
# UUID в BinExpr
# --------------------------------

def test_uuid_eq_serialization_with_uuid_object():
    expr = TestModel.uid == UUID("e801089b-c75b-11ed-aa56-ac1f6bd30991")

    result = expr.to_odata()

    assert result == (
        "Ref_Key eq guid'e801089b-c75b-11ed-aa56-ac1f6bd30991'"
    )


def test_uuid_eq_serialization_with_string():
    expr = TestModel.uid == "e801089b-c75b-11ed-aa56-ac1f6bd30991"

    result = expr.to_odata()

    assert result == (
        "Ref_Key eq guid'e801089b-c75b-11ed-aa56-ac1f6bd30991'"
    )


# --------------------------------
# contains() должен учитывать тип
# --------------------------------

def test_contains_uses_field_type():
    expr = TestModel.uid.contains("e801089b-c75b-11ed-aa56-ac1f6bd30991")

    result = expr.to_odata()

    assert result == (
        "contains(Ref_Key, guid'e801089b-c75b-11ed-aa56-ac1f6bd30991')"
    )


# --------------------------------
# Коллекции UUID
# --------------------------------

def test_uuid_collection_serialization():
    expr = TestModel.uid.in_([
        "e801089b-c75b-11ed-aa56-ac1f6bd30991",
        "11111111-1111-1111-1111-111111111111",
    ])

    result = expr.to_odata()

    assert result == (
        "Ref_Key in (guid'e801089b-c75b-11ed-aa56-ac1f6bd30991', "
        "guid'11111111-1111-1111-1111-111111111111')"
    )


# --------------------------------
# Обычные строки НЕ должны стать guid
# --------------------------------

def test_string_field_not_serialized_as_guid():
    expr = TestModel.name == "Test"

    result = expr.to_odata()

    assert result == "Description eq 'Test'"