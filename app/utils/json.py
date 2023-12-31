"""Contains JSON decoder class."""

import json
from typing import Any, Dict

import arrow
from bson import ObjectId


class JSONDecoder(json.JSONDecoder):
    """JSON decoder class."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialization method."""
        super().__init__(object_hook=self._object_hook, *args, **kwargs)

    def _object_hook(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Decodes datetime values."""
        for key, value in obj.items():
            if isinstance(value, str) and self._is_datetime(value):
                obj[key] = arrow.get(value).datetime
            elif isinstance(value, str) and ObjectId.is_valid(value):
                obj[key] = ObjectId(value)
        return obj

    @staticmethod
    def _is_datetime(value: str) -> bool:
        """Verifies string value can be converted to datetime type."""
        try:
            arrow.get(value)
            return True
        except arrow.parser.ParserError:
            return False
