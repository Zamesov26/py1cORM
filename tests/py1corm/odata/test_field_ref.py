from py1cORM.models.base import ODataModel
from py1cORM.models.fields import Field
from py1cORM.odata.query import kwargs_to_expr


class Employee(ODataModel):
    name: str = Field()


def test_builds_contains_function_when_method_is_called():
    expr = Employee.name.contains('Ivan')

    assert expr.to_odata() == "contains(name, 'Ivan')"


def test_builds_startswith_function_when_method_is_called():
    expr = Employee.name.startswith('Ivan')

    assert expr.to_odata() == "startswith(name, 'Ivan')"


def test_builds_endswith_function_when_method_is_called():
    expr = Employee.name.endswith('Ivan')

    assert expr.to_odata() == "endswith(name, 'Ivan')"


def test_builds_startswith_function_when_lookup_is_given():
    expr = kwargs_to_expr(Employee, {'name__startswith': 'Ivan'})

    assert expr.to_odata() == "startswith(name, 'Ivan')"


def test_builds_endswith_function_when_lookup_is_given():
    expr = kwargs_to_expr(Employee, {'name__endswith': 'Ivan'})

    assert expr.to_odata() == "endswith(name, 'Ivan')"
