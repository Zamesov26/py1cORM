from py1cORM.odata.expressions import BinExpr, FuncExpr


class FieldRef:
    def __init__(self, model, field_or_fields):
        self.model = model

        if isinstance(field_or_fields, list):
            self.fields = field_or_fields
        else:
            self.fields = [field_or_fields]

    @property
    def field(self):
        return self.fields[-1]

    @property
    def path(self):
        return '/'.join(f.odata_name for f in self.fields)

    def __getattr__(self, item):
        field = self.field

        if not field.is_relation:
            raise AttributeError(f"Cannot traverse scalar field '{field.attr_name}'")

        target_model = field.get_related_model()

        next_field = target_model._fields.get(item)
        if not next_field:
            raise AttributeError(f'{item} not found in {target_model.__name__}')

        return FieldRef(
            target_model,
            self.fields + [next_field],
        )

    def __eq__(self, other):
        return BinExpr(self, 'eq', other)

    def __ne__(self, other):
        return BinExpr(self, 'ne', other)

    def __gt__(self, other):
        return BinExpr(self, 'gt', other)

    def __lt__(self, other):
        return BinExpr(self, 'lt', other)

    def __ge__(self, other):
        return BinExpr(self, 'ge', other)

    def __le__(self, other):
        return BinExpr(self, 'le', other)


def like(field: FieldRef, pattern: str):
    return BinExpr(field, 'like', pattern)


def contains(field: FieldRef, value: str):
    return FuncExpr('contains', field, value)
