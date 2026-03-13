from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field

# -----------------------------
# 1 Дефолтное поведение
# -----------------------------


class DefaultModel(ODataModel):
    uid: str = Field(alias='Ref_Key')
    name: str = Field(alias='Description')

    class Meta:
        entity_name = 'Test'
        pk = 'uid'


def test_default_repr_shows_loaded_fields():
    raw = {
        'Ref_Key': '123',
        'Description': 'TestName',
    }

    obj = DefaultModel.from_raw(raw)

    text = repr(obj)

    assert "uid='123'" in text
    assert "name='TestName'" in text


# -----------------------------
# 2 repr_fields
# -----------------------------


class ReprFieldsModel(ODataModel):
    uid: str = Field(alias='Ref_Key')
    name: str = Field(alias='Description')
    extra: str = Field(alias='Extra')

    class Meta:
        entity_name = 'Test'
        repr_fields = ['uid', 'name']


def test_repr_fields_only_prints_selected_fields():
    raw = {
        'Ref_Key': '123',
        'Description': 'TestName',
        'Extra': 'Hidden',
    }

    obj = ReprFieldsModel.from_raw(raw)

    text = repr(obj)

    assert "uid='123'" in text
    assert "name='TestName'" in text
    assert 'extra=' not in text


# -----------------------------
# 3 __str__ override
# -----------------------------


class StrOverrideModel(ODataModel):
    uid: str = Field(alias='Ref_Key')
    name: str = Field(alias='Description')

    class Meta:
        entity_name = 'Test'

    def __str__(self):
        return f'{self.name}'


def test_str_override_is_used_in_repr():
    raw = {
        'Ref_Key': '123',
        'Description': 'TestName',
    }

    obj = StrOverrideModel.from_raw(raw)

    text = repr(obj)

    assert text == '<StrOverrideModel TestName>'


# -----------------------------
# 4 __str__ имеет приоритет
# -----------------------------


class StrAndReprFieldsModel(ODataModel):
    uid: str = Field(alias='Ref_Key')
    name: str = Field(alias='Description')

    class Meta:
        entity_name = 'Test'
        repr_fields = ['uid']

    def __str__(self):
        return 'STR_PRIORITY'


def test_str_has_priority_over_repr_fields():
    raw = {
        'Ref_Key': '123',
        'Description': 'TestName',
    }

    obj = StrAndReprFieldsModel.from_raw(raw)

    text = repr(obj)

    assert text == '<StrAndReprFieldsModel STR_PRIORITY>'
