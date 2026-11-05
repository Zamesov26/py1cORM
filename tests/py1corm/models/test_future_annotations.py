"""Проверить модели с отложленным вычислением аннотаций."""

from __future__ import annotations

from uuid import UUID

import pytest

from py1cORM import Mapped
from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field


class DeferredModel(ODataModel):
    """Модель с аннотациями, сохранёнными Python как строки."""

    uid: Mapped[UUID] = Field(alias='Ref_Key')


def test_resolves_mapped_value_type_from_deferred_annotation():
    field = DeferredModel._fields['uid']
    entity = DeferredModel.from_raw({'Ref_Key': '7ee70e84-1324-4a11-92c0-c3ab01a83d32'})

    assert field.annotation is UUID
    assert isinstance(entity.uid, UUID)


def test_rejects_deferred_annotation_when_value_type_cannot_be_resolved():
    with pytest.raises(TypeError, match='Cannot resolve annotations'):

        class InvalidDeferredModel(ODataModel):
            value: Mapped[MissingType] = Field(alias='Value')  # type: ignore[name-defined]  # noqa: F821
