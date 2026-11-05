"""Исключения, описывающие ошибки подключения и контракта ORM."""


class ClientConnectionError(ConnectionError):
    """Ошибка подключения к удалённому OData-сервису."""

    pass


class ODataError(Exception):
    """Базовая ошибка обработки ответа OData."""

    pass


class FieldNotLoadedError(AttributeError):
    """Обращение к полю модели, отсутствующему в загруженном ответе."""

    def __init__(self, model_name: str, field_name: str, loaded_fields: set[str]):
        message = (
            f"Field '{field_name}' was not loaded on '{model_name}'.\n"
            f'Loaded fields: {", ".join(sorted(loaded_fields)) or "none"}.\n'
            f'Use .select() to load this field.'
        )
        super().__init__(message)
