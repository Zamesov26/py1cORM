from uuid import UUID

from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Embedded, Field, ForeignKey

# ---------------------------
# Модели
# ---------------------------


class WorkCenterModel(ODataModel):
    uid: UUID | None = Field(alias='ВидРабочегоЦентра_Key')


class ProductStageModel(ODataModel):
    owner_id: UUID | None = Field(alias='Owner_Key')
    name: str = Field(alias='Description')

    work_centers: list[WorkCenterModel] = Embedded(
        model=WorkCenterModel,
        alias='ВидыРабочихЦентров',
    )


class ProductionModel(ODataModel):
    uid: UUID | None = Field(alias='Ref_Key')
    nomenclature_key: UUID | None = Field(alias='Номенклатура_Key')


class InputProductionModel(ODataModel):
    uid: UUID | None = Field(alias='Ref_Key')
    nomenclature_key: UUID | None = Field(alias='Номенклатура_Key')


class ResourceSpecificationsModel(ODataModel):
    uid_1c: UUID | None = Field(alias='Ref_Key')
    name: str = Field(alias='Description')

    productions: list[ProductionModel] = Embedded(
        model=ProductionModel,
        alias='ВыходныеИзделия',
    )

    input_productions: list[InputProductionModel] = Embedded(
        model=InputProductionModel,
        alias='МатериалыИУслуги',
    )

    product_stage: ProductStageModel | None = ForeignKey(
        model=ProductStageModel,
        alias='ОсновноеИзделиеЭтап',
        key_field='ОсновноеИзделиеЭтап_Key',
    )


# ---------------------------
# Реальный фрагмент ответа
# ---------------------------

RAW_RESPONSE = {
    'value': [
        {
            'Ref_Key': 'a8fb7556-c75f-11ed-aa56-ac1f6bd30991',
            'Description': '#РС#: Пленка СМК ПП синяя акрил 152,4х90',
            'ОсновноеИзделиеЭтап_Key': 'a93d6b5d-c75f-11ed-aa56-ac1f6bd30991',
            'ВыходныеИзделия': [
                {
                    'Ref_Key': 'a8fb7556-c75f-11ed-aa56-ac1f6bd30991',
                    'Номенклатура_Key': '27b5677c-c75c-11ed-aa56-ac1f6bd30991',
                }
            ],
            'МатериалыИУслуги': [
                {
                    'Ref_Key': 'a8fb7556-c75f-11ed-aa56-ac1f6bd30991',
                    'Номенклатура_Key': '9de0ad04-a5e7-11ec-aa3b-ac1f6bd30991',
                }
            ],
            'ОсновноеИзделиеЭтап': {
                'Owner_Key': 'a8fb7556-c75f-11ed-aa56-ac1f6bd30991',
                'Description': '#ЭП#: Пленка СМК ПП синяя акрил 152,4х90',
                'ВидыРабочихЦентров': [
                    {'ВидРабочегоЦентра_Key': 'c9345821-3660-11ec-aa35-ac1f6bd30991'}
                ],
            },
            'ExtraField': 'unexpected',
        }
    ]
}


def test_real_1c_response_parsing():
    items = [
        ResourceSpecificationsModel.from_raw(item) for item in RAW_RESPONSE['value']
    ]

    # --- список
    assert isinstance(items, list)
    assert len(items) == 1

    spec = items[0]

    # --- обычные поля
    assert spec.uid_1c == UUID('a8fb7556-c75f-11ed-aa56-ac1f6bd30991')
    assert '#РС#' in spec.name

    # --- extra
    assert spec.extra() == {'ExtraField': 'unexpected'}

    # --- embedded productions
    assert len(spec.productions) == 1
    prod = spec.productions[0]
    assert prod.nomenclature_key == UUID('27b5677c-c75c-11ed-aa56-ac1f6bd30991')

    # --- embedded input productions
    assert len(spec.input_productions) == 1
    input_prod = spec.input_productions[0]
    assert input_prod.nomenclature_key == UUID('9de0ad04-a5e7-11ec-aa3b-ac1f6bd30991')

    # --- ForeignKey key
    assert spec.product_stage.id == UUID('a93d6b5d-c75f-11ed-aa56-ac1f6bd30991')

    # --- ForeignKey expand
    stage = spec.product_stage._entity
    assert stage is not None
    assert stage.owner_id == UUID('a8fb7556-c75f-11ed-aa56-ac1f6bd30991')
    assert '#ЭП#' in stage.name

    # --- nested embedded inside expand
    assert len(stage.work_centers) == 1
    wc = stage.work_centers[0]
    assert wc.uid == UUID('c9345821-3660-11ec-aa35-ac1f6bd30991')
