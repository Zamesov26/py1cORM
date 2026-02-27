from py1cORM.odata.factories import Field, ForeignKey
from py1cORM.odata.models import ODataModel


class Parent(ODataModel):
    name: str = Field(alias="Name")
    
    class Meta:
        entity_name = "Parents"


class Category(ODataModel):
    name: str = Field(alias="Name")
    parent: Parent = ForeignKey(model=Parent, alias="Parent")
    
    class Meta:
        entity_name = "Categories"


class Product(ODataModel):
    name: str = Field(alias="Description")
    category: Category = ForeignKey(model=Category, alias="Category")
    
    class Meta:
        entity_name = "Products"

