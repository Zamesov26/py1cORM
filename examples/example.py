"""Пример описания моделей и чтения данных из OData-интерфейса 1С."""

import os
from uuid import UUID

from py1cORM.connection import ODataConnection
from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Embedded, Field, Mapped, Relationship

# -------------------------------
# 1. Описание моделей
# -------------------------------


class WorkCenterModel(ODataModel):
    """Вид рабочего центра из вложенной структуры этапа производства."""

    uid: Mapped[UUID | None] = Field(alias='ВидРабочегоЦентра_Key')
    name: Mapped[str] = Field(alias='Description')


class ProductStageModel(ODataModel):
    """Этап производства с доступными видами рабочих центров."""

    owner_id: Mapped[UUID | None] = Field(alias='Owner_Key')
    work_centers: Mapped[list[WorkCenterModel]] = Embedded(
        model=WorkCenterModel,
        alias='ВидыРабочихЦентров',
    )

    class Meta:
        entity_name = 'Document_ЭтапПроизводства2_2'


class ProductionModel(ODataModel):
    """Строка изделия или материала ресурсной спецификации."""

    uid: Mapped[UUID | None] = Field(alias='Ref_Key')
    nomenclature_key: Mapped[UUID | None] = Field(alias='Номенклатура_Key')


class ResourceSpecificationsModel(ODataModel):
    """Ресурсная спецификация с изделиями, материалами и этапом производства."""

    uid_1c: Mapped[UUID | None] = Field(alias='Ref_Key')
    name: Mapped[str] = Field(alias='Description')

    productions: Mapped[list[ProductionModel]] = Embedded(
        model=ProductionModel,
        alias='ВыходныеИзделия',
    )

    input_productions: Mapped[list[ProductionModel]] = Embedded(
        model=ProductionModel,
        alias='МатериалыИУслуги',
    )

    product_stage_id: Mapped[UUID | None] = Field(alias='ОсновноеИзделиеЭтап_Key')
    product_stage: Mapped[ProductStageModel | None] = Relationship(
        model=ProductStageModel,
        alias='ОсновноеИзделиеЭтап',
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
        print('Stage key:', item.product_stage_id)
        if item.product_stage is not None:
            print('Owner:', item.product_stage.owner_id)
            print('Work centers:', len(item.product_stage.work_centers))
