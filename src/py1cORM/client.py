import requests
from requests.auth import HTTPBasicAuth

from py1cORM.odata.manager import Manager
from py1cORM.odata.query import QuerySpec


class ODataClient:
    def __init__(
        self,
        *,
        host: str,
        database: str,
        username: str,
        password: str,
        models: list[type],
    ):
        self.host = host.rstrip("/")
        self.database = database
        self.auth = HTTPBasicAuth(username, password)
        
        self.base_url = (
            f"{self.host}/{self.database}/odata/standard.odata"
        )
        
        # регистрация моделей
        for model in models:
            self._register_model(model)
    
    # -----------------------------
    # Регистрация модели
    # -----------------------------
    
    def _register_model(self, model):
        name = model.__name__.replace("Model", "").lower()
        manager = Manager(self, model)
        setattr(self, name, manager)
    
    # -----------------------------
    # Выполнение запроса
    # -----------------------------
    
    def get_collection(self, entity_name: str, spec: QuerySpec):
        url = f"{self.base_url}/{entity_name}"
        
        params = {}
        
        if spec.select:
            params["$select"] = ",".join(spec.select)
        
        if spec.expand:
            params["$expand"] = ",".join(spec.expand)
        
        if spec.filter:
            params["$filter"] = spec.filter
        
        if spec.orderby:
            params["$orderby"] = ",".join(spec.orderby)
        
        if spec.top is not None:
            params["$top"] = spec.top
        
        if spec.skip is not None:
            params["$skip"] = spec.skip
        
        params["$format"] = "json"
        
        response = requests.get(
            url,
            params=params,
            auth=self.auth,
        )
        print("params:", params)
        print("REQUEST URL:", response.url)
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)
        
        response.raise_for_status()
        
        data = response.json()
        
        return data.get("value", [])
