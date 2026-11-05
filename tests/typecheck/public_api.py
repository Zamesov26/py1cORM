"""Проверить вывод типов декларативных моделей без плагинов анализаторов."""

from typing import TYPE_CHECKING, assert_type
from uuid import UUID

from py1cORM import Mapped
from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Embedded, Field, Relationship
from py1cORM.odata.expressions import BinExpr
from py1cORM.odata.fields import FieldRef
from py1cORM.odata.query import QuerySet


class ParentCategory(ODataModel):
    """Родительская категория для проверки глубокого пути."""

    name: Mapped[str] = Field(alias='Description')


class Category(ODataModel):
    """Связанная модель для проверки отношения."""

    name: Mapped[str] = Field(alias='Description')
    parent: Mapped[ParentCategory | None] = Relationship(
        model=ParentCategory,
        alias='Parent',
    )


class Row(ODataModel):
    """Вложенная модель для проверки коллекции."""

    quantity: Mapped[int] = Field(alias='Quantity')


class Product(ODataModel):
    """Модель, покрывающая основные варианты декларативных полей."""

    uid: Mapped[UUID] = Field(alias='Ref_Key')
    name: Mapped[str] = Field(alias='Description')
    category_id: Mapped[UUID | None] = Field(alias='Category_Key')
    category: Mapped[Category | None] = Relationship(
        model=Category,
        alias='Category',
    )
    rows: Mapped[list[Row]] = Embedded(model=Row, alias='Rows')

    class Meta:
        """Настройки тестовой OData-модели."""

        entity_name = 'Catalog_Products'


assert_type(Product.uid, FieldRef[Product, UUID])
assert_type(Product.name, FieldRef[Product, str])
assert_type(Product.category_id, FieldRef[Product, UUID | None])
assert_type(Product.category, FieldRef[Product, Category | None])
assert_type(Product.rows, FieldRef[Product, list[Row]])
assert_type(Product.category.then(Category.name), FieldRef[Category, str])
assert_type(
    Product.category.then(Category.parent).then(ParentCategory.name),
    FieldRef[ParentCategory, str],
)
assert_type(Product.uid == UUID(int=1), BinExpr)

if TYPE_CHECKING:
    # Поле другой модели должно отклоняться статическим анализатором.
    Product.category.then(Row.quantity)  # type: ignore[arg-type]

product = Product.from_raw({'Ref_Key': '7ee70e84-1324-4a11-92c0-c3ab01a83d32'})
assert_type(product, Product)
assert_type(product.uid, UUID)
assert_type(product.name, str)
assert_type(product.category_id, UUID | None)
assert_type(product.category, Category | None)
assert_type(product.rows, list[Row])

query = QuerySet(None, Product)
assert_type(query, QuerySet[Product])
assert_type(query.all(), list[Product])
