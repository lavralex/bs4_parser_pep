class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    pass


class VersionListNotFoundException(Exception):
    """Вызывается, когда при парсинге
    версий не найден список c версиями Python."""
    pass


class NoResponseException(Exception):
    """Вызывается, когда по URL нет ответа."""
    pass
