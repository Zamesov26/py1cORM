# from typing import TYPE_CHECKING
#
# from py1cORM.odata.manager import Manager
# if TYPE_CHECKING:
#     from odata.models import ODataModel
#
#
# class ODataClient:
#     def __init__(self, base_url, auth=None):
#         self.base_url = base_url
#         self.auth = auth
#
#     def bind(self, model: type["ODataModel"]):
#         model._bind_fields()
#         model.objects = Manager(self, model)
#         return model