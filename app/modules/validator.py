from __future__ import annotations

from app.core.config import Settings
from app.core.errors import ValidationError
from app.core.utils import compact_query


class InputValidator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def validate(self, query: str) -> str:
        normalized = compact_query(query)
        if len(normalized) < self.settings.min_query_len:
            raise ValidationError("Запрос слишком короткий. Уточни тему исследования.")
        return normalized
