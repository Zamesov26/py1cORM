from pydantic import BaseModel

from PyOData1C.odata.fields import FieldRef

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
        cls.f = FieldsNamespace(cls)
        return cls
    
    def __getattr__(cls, item):
        fields = cls.__dict__.get("__pydantic_fields__", {})
        if item in fields:
            field = fields[item]
            return FieldRef(cls, field)
        raise AttributeError(item)


class ODataModel(BaseModel, metaclass=ODataModelMeta):
    pass
