from typing import TYPE_CHECKING

from py1cORM.odata.query import QuerySet

if TYPE_CHECKING:
    pass
    
class Manager:
    def __init__(self, client, model):
        self.client = client
        self.model = model

    def all(self): return QuerySet(self.client, self.model).all()
    def filter(self, expr): return QuerySet(self.client, self.model).filter(expr)
    def select(self, *fields): return QuerySet(self.client, self.model).select(*fields)
    def expand(self, *fields): return QuerySet(self.client, self.model).expand(*fields)
    def get(self, **kwargs): return QuerySet(self.client, self.model).get(**kwargs)
