from uuid import UUID

from py1cORM.client import ODataClient
from py1cORM.odata.factories import Field
from py1cORM.odata.models import ODataModel


# -------------------------------
# 1. Описание модели
# -------------------------------

class NomenclatureModel(ODataModel):
    uid_1c: UUID = Field(alias="Ref_Key")
    name: str = Field(alias="Description")
    unit_measurement_key: str | None= Field(alias="ЕдиницаИзмерения_Key")
    article: str = Field(alias="Артикул")
    
    class Meta:
        entity_name = "Catalog_Номенклатура"
        pk = "uid_1c"


# -------------------------------
# 2. Создаем клиент (фасад)
# -------------------------------

client = ODataClient(
    host="http://192.168.0.18",
    database="erp_dev",
    username="bp",
    password="HR2p9OE3XV",
    models=[NomenclatureModel],
)

# -------------------------------
# 3. Использование
# -------------------------------

items = (
    client.nomenclature
    .select(NomenclatureModel.name)
    .all()
)

for item in items:
    print(item)
