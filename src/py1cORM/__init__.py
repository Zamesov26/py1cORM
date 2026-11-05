"""Python ORM for the 1C OData interface."""

from importlib.metadata import PackageNotFoundError, version

from py1cORM.models.fields import Mapped

try:
    __version__ = version('py1cORM')
except PackageNotFoundError:
    __version__ = '0+unknown'

__all__ = ['Mapped', '__version__']
