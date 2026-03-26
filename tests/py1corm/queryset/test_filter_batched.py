from unittest.mock import Mock
from uuid import UUID

from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field
from py1cORM.odata.expressions import AND
from py1cORM.odata.fields import like
from py1cORM.odata.query import QuerySet


class NomenclatureModel(ODataModel):
    uid: UUID = Field(alias='Ref_Key')
    name: str = Field(alias='Description')
    article: str = Field(alias='Артикул')
    version: str = Field(alias='DataVersion')

    is_folder: bool = Field(alias='IsFolder')
    is_deleted: bool = Field(alias='DeletionMark')

    unit_measurement_key: str = Field(alias='ЕдиницаИзмерения_Key')

    class Meta:
        entity_name = 'Catalog_Номенклатура'


def test_batched_builds_filter_and_pagination():
    client = Mock()

    client.get_collection.side_effect = [
        [{'id': 1}, {'id': 2}],  # batch 1
        [{'id': 3}],  # batch 2
        [],  # stop
    ]

    qs = QuerySet(client=client, model=NomenclatureModel).filter(
        AND(
            NomenclatureModel.is_deleted == False,  # noqa: E712
            NomenclatureModel.is_folder == False,  # noqa: E712
            like(NomenclatureModel.name, 'Стакан%'),
        )
    )

    result = list(qs.batched(batch_size=2))

    # ---------------------------
    # вызовы
    # ---------------------------
    assert client.get_collection.call_count == 3

    first_call = client.get_collection.call_args_list[0][0]
    second_call = client.get_collection.call_args_list[1][0]

    spec1 = first_call[1]
    spec2 = second_call[1]

    # ---------------------------
    # pagination
    # ---------------------------
    assert spec1.top == 2
    assert spec1.skip == 0

    assert spec2.top == 2
    assert spec2.skip == 2

    # ---------------------------
    # filter
    # ---------------------------
    assert spec1.filter is not None

    assert spec1.filter == (
        "(DeletionMark eq false and IsFolder eq false and like(Description, 'Стакан%'))"
    )

    # ---------------------------
    # результат (батчи!)
    # ---------------------------
    assert len(result) == 2
    assert [len(batch) for batch in result] == [2, 1]

    # дополнительно проверим, что данные не потерялись
    flat = [item for batch in result for item in batch]
    assert len(flat) == 3
