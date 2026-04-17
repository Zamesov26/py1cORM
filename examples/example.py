import os
from uuid import UUID

from py1cORM.connection import ODataConnection
from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Embedded, Field, ForeignKey

# -------------------------------
# 1. Описание моделей
# -------------------------------


class WorkCenterModel(ODataModel):
    uid: UUID | None = Field(alias='ВидРабочегоЦентра_Key')
    name: str = Field(alias='Description')


class ProductStageModel(ODataModel):
    owner_id: UUID | None = Field(alias='Owner_Key')
    work_centers: list[WorkCenterModel] = Embedded(
        model=WorkCenterModel,
        alias='ВидыРабочихЦентров',
    )

    class Meta:
        entity_name = 'Document_ЭтапПроизводства2_2'


class ProductionModel(ODataModel):
    uid: UUID | None = Field(alias='Ref_Key')
    nomenclature_key: UUID | None = Field(alias='Номенклатура_Key')


class ResourceSpecificationsModel(ODataModel):
    uid_1c: UUID | None = Field(alias='Ref_Key')
    name: str = Field(alias='Description')

    productions: list[ProductionModel] = Embedded(
        model=ProductionModel,
        alias='ВыходныеИзделия',
    )

    input_productions: list[ProductionModel] = Embedded(
        model=ProductionModel,
        alias='МатериалыИУслуги',
    )

    product_stage: ProductStageModel | None = ForeignKey(
        model=ProductStageModel,
        alias='ОсновноеИзделиеЭтап',
        key_field='ОсновноеИзделиеЭтап_Key',
    )

    class Meta:
        entity_name = 'Catalog_РесурсныеСпецификации'


# -------------------------------
# 2. Создание коннектора
# -------------------------------

conn = ODataConnection(
    host=os.getenv('HOST'),
    database=os.getenv('DATABASE'),
    username=os.getenv('USERNAME'),
    password=os.getenv('PASSWORD'),
)

# -------------------------------
# 3. Использование
# -------------------------------

specs = ResourceSpecificationsModel.using(conn)

# 🔹 Простой select
items = specs.select(ResourceSpecificationsModel.name).paginate(top=5).all()

for item in items:
    print('Name:', item.name)
    print('Extra:', item.extra())
    print('-----')


# 🔹 Пример с expand
items_with_stage = (
    specs.expand(ResourceSpecificationsModel.product_stage).paginate(top=3).all()
)

for item in items_with_stage:
    if item.is_loaded('product_stage'):
        fk = item.product_stage
        print('Stage key:', fk.id)

        if fk.is_loaded():
            print('Owner:', fk.owner_id)
            print('Work centers:', len(fk.work_centers))
