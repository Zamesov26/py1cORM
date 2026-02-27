from pydantic import BaseModel, ConfigDict

from py1cORM.odata.fields import FieldRef, ODataFieldInfo


class FieldsNamespace:
    def __init__(self, model):
        self.model = model
    
    def __getattr__(self, item):
        field = self.model.model_fields[item]
        alias = field.alias or item
        return FieldRef(self.model, item, alias)





class ODataModelMeta(type(BaseModel)):
    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)
        
        # bind поля
        for field_name, field in cls.__dict__.get(
            "__pydantic_fields__", {}
        ).items():
            if hasattr(field, "bind"):
                field.bind(cls, field_name)
        
        return cls
    
    def __getattr__(cls, item):
        fields = cls.__dict__.get("__pydantic_fields__", {})
        
        if item in fields:
            return fields[item].ref()
        
        raise AttributeError(item)




class ODataModel(BaseModel, metaclass=ODataModelMeta):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )
    class Meta:
        entity_name: str
