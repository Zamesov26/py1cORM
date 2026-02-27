from pydantic import BaseModel

from odata.fields import ODataFieldInfo


class ODataModel(BaseModel):
    """
    Базовая модель для OData ORM.
    """
    
    class Meta:
        entity_name: str | None = None
    
    objects = None
    
    @classmethod
    def _fields(cls):
        return {
            name: field
            for name, field in cls.__dict__.items()
            if isinstance(field, ODataFieldInfo)
        }
    
    @classmethod
    def _bind_fields(cls):
        """
        Биндим поля к модели:
        - записываем model и attr_name
        - делаем Model.field доступным как FieldRef
        """
        for attr_name, field in cls.model_fields.items():
            field.bind(cls, attr_name)
            
            # заменяем атрибут класса на FieldRef
            setattr(cls, attr_name, field.ref())
    
    @classmethod
    def _get_entity_name(cls):
        if not cls.Meta.entity_name:
            raise ValueError(f"{cls.__name__}.Meta.entity_name is not defined")
        return cls.Meta.entity_name
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.model_dump()}>"
