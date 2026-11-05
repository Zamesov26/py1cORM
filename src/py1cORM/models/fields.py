"""Типизированные дескрипторы полей и связей OData."""

from __future__ import annotations

from typing import Any, overload

from py1cORM.exceptions import FieldNotLoadedError
from py1cORM.odata.fields import FieldRef
from py1cORM.parser.sentinels import NotLoaded


class Mapped[T]:
    """Тип ORM-атрибута со значением ``T`` у экземпляра модели."""

    @overload
    def __get__[ModelT](
        self, instance: None, owner: type[ModelT]
    ) -> FieldRef[ModelT, T]: ...

    @overload
    def __get__(self, instance: object, owner: type) -> T: ...

    def __get__[ModelT](
        self, instance: object | None, owner: type[ModelT]
    ) -> FieldRef[ModelT, T] | T:
        raise NotImplementedError


class Field[T](Mapped[T]):
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
        default: T | None = None,
    ) -> None:
        self.entity_type = entity_type
        self.alias = alias
        self.odata_name = odata_name or alias
        self.auto_expand = auto_expand
        self.default = default
        self.model: type | None = None
        self.attr_name: str | None = None
        self.annotation: Any = None

    def bind(self, model: type, attr_name: str, annotation: Any) -> Field[T]:
        """Связать поле с моделью, Python-именем и типом значения."""
        self.model = model
        self.attr_name = attr_name
        self.annotation = annotation
        if not self.odata_name:
            self.odata_name = self.alias or attr_name
        if not self.alias:
            self.alias = self.odata_name
        return self

    @overload
    def __get__[ModelT](
        self, instance: None, owner: type[ModelT]
    ) -> FieldRef[ModelT, T]: ...

    @overload
    def __get__(self, instance: object, owner: type) -> T: ...

    def __get__[ModelT](
        self, instance: object | None, owner: type[ModelT]
    ) -> FieldRef[ModelT, T] | T:
        if instance is None:
            return FieldRef(owner, self)
        if self.attr_name is None:
            raise AttributeError('Field is not bound to a model')
        value = instance.__dict__.get(self.attr_name, NotLoaded)
        if value is NotLoaded:
            loaded = instance.__dict__.get('_loaded_fields', set())
            raise FieldNotLoadedError(owner.__name__, self.attr_name, loaded)
        return value

    def __set__(self, instance: object, value: T | object) -> None:
        if self.attr_name is None:
            raise AttributeError('Field is not bound to a model')
        instance.__dict__[self.attr_name] = value

    def ref(self) -> FieldRef[object, T]:
        """Вернуть ссылку на поле для построения OData-выражений."""
        return FieldRef(self.model, self)

    def get_related_model(self) -> type:
        """Сообщить, что скалярное поле не содержит связанную модель."""
        raise AttributeError(f"Field '{self.attr_name}' is not a relation")


class TypedGuid[T](Field[T]):
    """GUID-поле, сериализуемое с явным типом сущности 1С."""

    def serialize_filter(self, value: object) -> str:
        """Сериализовать GUID для типизированного фильтра 1С."""
        return f"cast(guid'{value}', '{self.entity_type}')"


class Embedded[T](Field[T]):
    """Встроенная структура или коллекция объектов в ответе OData."""

    is_relation = True
    is_embedded = True

    def __init__(self, *, model: type, expand_only: bool = False, **kwargs: Any):
        super().__init__(**kwargs)
        self.embedded_model = model
        self.expand_only = expand_only

    def get_related_model(self) -> type:
        """Вернуть модель элементов встроенной структуры."""
        return self.embedded_model


class Relationship[T](Field[T | None]):
    """Связанная сущность, загружаемая через ``$expand``."""

    is_relation = True
    is_foreign_key = True

    def __init__(self, *, model: type[T], **kwargs: Any):
        super().__init__(**kwargs)
        self.related_model = model

    def get_related_model(self) -> type[T]:
        """Вернуть модель связанной сущности."""
        return self.related_model


class Navigation[T](Field[T]):
    """Навигационное свойство OData без собственного GUID."""

    is_relation = True
    is_navigation = True

    def __init__(self, *, model: type, **kwargs: Any):
        super().__init__(**kwargs)
        self.related_model = model

    def get_related_model(self) -> type:
        """Вернуть модель навигационного свойства."""
        return self.related_model
