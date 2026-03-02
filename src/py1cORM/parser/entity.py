from uuid import UUID

from py1cORM.exceptions import FieldNotLoadedError
from py1cORM.models.fields import ForeignKey
from py1cORM.models.relations import FK
from py1cORM.parser.convert import convert
from py1cORM.parser.sentinels import NotLoaded


class Entity:
    def __init__(self, model_cls, raw: dict):
        self._model = model_cls
        self._extra = {}
        self._loaded_fields = set()

        for field_name, field in model_cls._fields.items():
            # -------------------------
            # ForeignKey
            # -------------------------
            if isinstance(field, ForeignKey):
                key_raw = raw.get(field.key_field)

                key_value = None
                if key_raw:
                    key_value = convert(key_raw, UUID)

                entity_value = None
                if field.alias in raw and isinstance(raw[field.alias], dict):
                    entity_value = field.related_model.from_raw(raw[field.alias])

                if key_raw is None and field.alias not in raw:
                    object.__setattr__(self, field_name, NotLoaded)
                    continue

                fk = FK(key=key_value, entity=entity_value)

                object.__setattr__(self, field_name, fk)
                self._loaded_fields.add(field_name)
                continue

            # -------------------------
            # Обычные поля
            # -------------------------
            alias = field.alias

            if alias in raw:
                raw_value = raw[alias]
                value = convert(raw_value, field.annotation)
                object.__setattr__(self, field_name, value)
                self._loaded_fields.add(field_name)
            else:
                object.__setattr__(self, field_name, NotLoaded)

        for key, value in raw.items():
            if key not in model_cls._alias_map:
                self._extra[key] = value

    def extra(self):
        return dict(self._extra)

    def __getattribute__(self, item):
        value = object.__getattribute__(self, item)

        if value is NotLoaded:
            model = object.__getattribute__(self, '_model')
            loaded = object.__getattribute__(self, '_loaded_fields')
            raise FieldNotLoadedError(model.__name__, item, loaded)

        return value

    def is_loaded(self, field_name: str) -> bool:
        return field_name in self._loaded_fields
