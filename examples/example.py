from uuid import UUID

from pydantic import UUID1

from py1cORM.connection import ODataConnection
from py1cORM.odata.factories import Field
from py1cORM.odata.models import ODataModel


# -------------------------------
# 1. Описание модели
# -------------------------------

class WorkCenterModel(ODataModel):
    uid: str = Field(alias='ВидРабочегоЦентра_Key')


class ProductStageModel(ODataModel):
    owner_id: str = Field(alias='Owner_Key')
    work_centers: list[WorkCenterModel] = Field(alias='ВидыРабочихЦентров')


class ProductionModel(ODataModel):
    uid: str = Field(alias='Ref_Key')
    nomenclature_key: str = Field(alias='Номенклатура_Key')


class ResourceSpecificationsModel(ODataModel):
    uid_1c: UUID1 = Field(alias='Ref_Key')
    name: str = Field(alias='Description')
    productions: list[ProductionModel] = Field(alias='ВыходныеИзделия')
    input_productions: list[ProductionModel] = Field(alias='МатериалыИУслуги')
    product_stage: ProductStageModel = Field(alias='ОсновноеИзделиеЭтап',)
    

    class Meta:
        entity_name = 'Catalog_РесурсныеСпецификации'

# -------------------------------
# 1. Создание коннектора
# -------------------------------

conn = ODataConnection(
    host="http://192.168.0.18",
    database="erp_dev",
    username="bp",
    password="HR2p9OE3XV",
)

# -------------------------------
# 3. Использование
# -------------------------------

nomenclature = ResourceSpecificationsModel.using(conn)

items = (
    nomenclature
    .select(ResourceSpecificationsModel.name)
    .all()
)
for item in items:
    print(item)
