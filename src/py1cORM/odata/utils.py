"""Преобразование Python-ссылок и имён полей в пути OData."""

from py1cORM.odata.fields import FieldRef


def build_fieldref_from_string(model, field: str) -> FieldRef:
    """Построить ссылку на поле из пути с разделителем ``__``."""
    parts = field.split('__')
    current_model = model
    fields = []

    for i, part in enumerate(parts):
        model_fields = current_model._fields

        if part not in model_fields:
            raise ValueError(
                f"Unknown field '{part}' for model {current_model.__name__}"
            )

        field_obj = model_fields[part]
        fields.append(field_obj)

        if field_obj.is_relation:
            current_model = field_obj.get_related_model()
        else:
            if i != len(parts) - 1:
                raise ValueError(f"Cannot traverse through scalar field '{part}'")

    return FieldRef(model, fields)


def field_to_path(model, field):
    """Преобразовать имя или ссылку на поле в путь OData."""
    if isinstance(field, FieldRef):
        return field.path

    if isinstance(field, str):
        return build_fieldref_from_string(model, field).path

    raise TypeError(f'Unsupported field type: {type(field)}')


def order_to_odata(model, field):
    """Преобразовать описание сортировки в выражение ``$orderby``."""
    if isinstance(field, tuple):
        if len(field) != 2:
            raise ValueError('Order tuple must contain field and direction')
        name, direction = field
        if direction not in {'asc', 'desc'}:
            raise ValueError("Order direction must be 'asc' or 'desc'")
        path = field_to_path(model, name)
        return f'{path} {direction}'
    return field_to_path(model, field)
