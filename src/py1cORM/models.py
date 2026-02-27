from pydantic import BaseModel, ConfigDict

from py1cORM.odata.models import ODataModelMeta


class ODataModel(BaseModel, metaclass=ODataModelMeta):
    model_config = ConfigDict(
        populate_by_name=True,
        extra="ignore",
    )
    
    class Meta:
        entity_name: str | None = None
    
    objects = None
    
    @classmethod
    def _bind_fields(cls):
        # только bind, БЕЗ setattr
        for attr_name, field in cls.model_fields.items():
            field.bind(cls, attr_name)
    
    @classmethod
    def _get_entity_name(cls):
        if not cls.Meta.entity_name:
            raise ValueError(
                f"{cls.__name__}.Meta.entity_name is not defined"
            )
        return cls.Meta.entity_name
    
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.model_dump()}>"

