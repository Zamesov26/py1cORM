from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field, ForeignKey


class Parent(ODataModel):
    name: str = Field(alias='Name')

    class Meta:
        entity_name = 'Parents'
        pk = 'name'  # если нет id — можно не указывать


class Category(ODataModel):
    name: str = Field(alias='Name')

    parent: Parent | None = ForeignKey(
        model=Parent,
        alias='Parent',
        key_field='Parent_Key',  # ВАЖНО
    )

    class Meta:
        entity_name = 'Categories'
        pk = 'name'


class Product(ODataModel):
    name: str = Field(alias='Description')

    category: Category | None = ForeignKey(
        model=Category,
        alias='Category',
        key_field='Category_Key',  # ВАЖНО
    )

    class Meta:
        entity_name = 'Products'
        pk = 'name'
