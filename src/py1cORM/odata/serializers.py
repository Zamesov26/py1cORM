from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

def serialize_value(value):
    # выражения
    if hasattr(value, "to_odata"):
        return value.to_odata()
    
    # None
    if value is None:
        return "null"
    
    # bool
    if isinstance(value, bool):
        return "true" if value else "false"
    
    # int / float
    if isinstance(value, (int, float)):
        return str(value)
    
    # Decimal
    if isinstance(value, Decimal):
        return str(value)
    
    # UUID
    if isinstance(value, UUID):
        return f"guid'{value}'"
    
    # datetime
    if isinstance(value, datetime):
        # ISO без микросекунд
        iso = value.replace(microsecond=0).isoformat()
        return f"datetime'{iso}'"
    
    # date
    if isinstance(value, date):
        return f"date'{value.isoformat()}'"
    
    # str
    if isinstance(value, str):
        escaped = value.replace("'", "''")
        return f"'{escaped}'"
    
    # список (например future IN)
    if isinstance(value, (list, tuple, set)):
        serialized = ", ".join(serialize_value(v) for v in value)
        return f"({serialized})"
    
    raise TypeError(f"Unsupported type for OData serialization: {type(value)}")
