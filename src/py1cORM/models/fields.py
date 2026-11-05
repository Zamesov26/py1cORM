"""Декларативные поля моделей и описания связей OData."""

from typing import Any, TypeVar

from py1cORM.odata.fields import FieldRef

T = TypeVar('T')


class Field[T]:
    """Скалярное поле модели с сопоставлением имени из ответа OData."""

    is_relation = False
    is_embedded = False
    is_foreign_key = False

    def __init__(
        self,
        *,
        alias: str | None = None,
        odata_name: str | None = None,
        auto_expand: bool = False,
        entity_type: str | None = None,
        default=None,
    ):

        self.entity_type = entity_type
        self.alias = alias
        self.odata_name = odata_name or alias
        self.auto_expand = auto_expand
        self.default = default

        self.model: type | None = None
        self.attr_name: str | None = None
        self.annotation: Any = None

    def bind(self, model, attr_name: str, annotation):
        """Связать поле с моделью, Python-именем и аннотацией типа."""
        self.model = model
        self.attr_name = attr_name
        self.annotation = annotation

        if not self.odata_name:
            self.odata_name = self.alias or attr_name

        return self

    def ref(self) -> FieldRef[T]:
        """Вернуть ссылку на поле для построения OData-выражений."""
        return FieldRef(self.model, self)

    def get_related_model(self):
        """Сообщить, что скалярное поле не содержит связанную модель."""
        raise AttributeError(f"Field '{self.attr_name}' is not a relation")


class TypedGuid(Field):
    """GUID-поле, сериализуемое с явным типом сущности 1С."""

    def __init__(
        self,
        *,
        entity_type,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.entity_type = entity_type

    def serialize_filter(self, value):
        """Сериализовать GUID для типизированного фильтра 1С."""
        return f"cast(guid'{value}', '{self.entity_type}')"


class Embedded(Field):
    """Встроенная структура или коллекция объектов в ответе OData."""

    is_relation = True
    is_embedded = True

    def __init__(self, *, model: type, expand_only=False, **kwargs):
        super().__init__(**kwargs)
        self.embedded_model = model
        self.expand_only = expand_only

    def get_related_model(self):
        """Вернуть модель элементов встроенной структуры."""
        return self.embedded_model


class ForeignKey(Field):
    """Связь по GUID с возможностью загрузки сущности через ``$expand``."""

    is_relation = True
    is_foreign_key = True

    def __init__(self, *, model: Any, key_field: str, **kwargs):
        super().__init__(**kwargs)
        self.related_model = model
        self.key_field = key_field

    def get_related_model(self):
        """Вернуть модель связанной сущности."""
        return self.related_model


class Navigation(Field):
    """Навигационное свойство OData без собственного GUID.

    Значение может быть загружено через ``$expand`` или navigation link URL.
    """

    is_relation = True
    is_navigation = True

    def __init__(self, *, model: type, **kwargs):
        super().__init__(**kwargs)
        self.related_model = model

    def get_related_model(self):
        """Вернуть модель навигационного свойства."""
        return self.related_model
