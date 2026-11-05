from uuid import UUID

from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field, Mapped, Relationship


class Parent(ODataModel):
    name: Mapped[str] = Field(alias='Name')

    class Meta:
        entity_name = 'Parents'
        pk = 'name'  # если нет id — можно не указывать


class Category(ODataModel):
    name: Mapped[str] = Field(alias='Name')

    parent_id: Mapped[UUID | None] = Field(alias='Parent_Key')
    parent: Mapped[Parent | None] = Relationship(
        model=Parent,
        alias='Parent',
    )

    class Meta:
        entity_name = 'Categories'
        pk = 'name'


class Product(ODataModel):
    uid_1c: Mapped[UUID] = Field(alias='Ref_Key')
    name: Mapped[str] = Field(alias='Description')

    category_id: Mapped[UUID | None] = Field(alias='Category_Key')
    category: Mapped[Category | None] = Relationship(
        model=Category,
        alias='Category',
    )

    class Meta:
        entity_name = 'Products'
        pk = 'name'
