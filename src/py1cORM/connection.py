import requests
from requests.auth import HTTPBasicAuth

from py1cORM.odata.query import QuerySpec


class ODataConnection:
    def __init__(
        self,
        *,
        host: str,
        database: str,
        username: str,
        password: str,
    ):
        self.host = host.rstrip("/")
        self.database = database
        self.auth = HTTPBasicAuth(username, password)
        
        self.base_url = (
            f"{self.host}/{self.database}/odata/standard.odata"
        )
    
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
        
        response.raise_for_status()
        
        data = response.json()
        
        return data.get("value", [])
