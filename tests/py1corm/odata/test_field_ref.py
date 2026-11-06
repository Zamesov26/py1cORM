import pytest

from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field, Mapped, Relationship
from py1cORM.odata.query import kwargs_to_expr


class Employee(ODataModel):
    name: Mapped[str] = Field()
    active: Mapped[bool] = Field()


class Department(ODataModel):
    name: Mapped[str] = Field()


class Assignment(ODataModel):
    employee: Mapped[Employee | None] = Relationship(model=Employee)


def test_builds_contains_function_when_method_is_called():
    expr = Employee.name.contains('Ivan')

    assert expr.to_odata() == "contains(name, 'Ivan')"


def test_builds_startswith_function_when_method_is_called():
    expr = Employee.name.startswith('Ivan')

    assert expr.to_odata() == "startswith(name, 'Ivan')"


def test_builds_endswith_function_when_method_is_called():
    expr = Employee.name.endswith('Ivan')

    assert expr.to_odata() == "endswith(name, 'Ivan')"


def test_builds_eq_expression_when_method_is_called():
    expr = Employee.active.eq(False)

    assert expr.to_odata() == 'active eq false'


def test_builds_ne_expression_when_method_is_called():
    expr = Employee.active.ne(True)

    assert expr.to_odata() == 'active ne true'


def test_builds_startswith_function_when_lookup_is_given():
    expr = kwargs_to_expr(Employee, {'name__startswith': 'Ivan'})

    assert expr.to_odata() == "startswith(name, 'Ivan')"


def test_builds_endswith_function_when_lookup_is_given():
    expr = kwargs_to_expr(Employee, {'name__endswith': 'Ivan'})

    assert expr.to_odata() == "endswith(name, 'Ivan')"


def test_rejects_field_from_unrelated_model_when_path_is_built():
    with pytest.raises(ValueError, match='belongs to Department, expected Employee'):
        Assignment.employee.then(Department.name)  # type: ignore[arg-type]
