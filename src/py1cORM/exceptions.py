class ClientConnectionError(ConnectionError):
    pass


class ODataError(Exception):
    pass


class FieldNotLoadedError(AttributeError):
    def __init__(self, model_name: str, field_name: str, loaded_fields: set[str]):
        message = (
            f"Field '{field_name}' was not loaded on '{model_name}'.\n"
            f'Loaded fields: {", ".join(sorted(loaded_fields)) or "none"}.\n'
            f'Use .select() to load this field.'
        )
        super().__init__(message)
