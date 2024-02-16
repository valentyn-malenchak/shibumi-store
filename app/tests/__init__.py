"""Module that contains base test component."""

from typing import Any, List


class BaseTest:
    """Base test class."""

    def _exclude_fields(
        self,
        obj_: Any,
        *,
        exclude_keys: List[str],
    ) -> Any:
        """Excludes specified keys from dictionaries."""

        if isinstance(obj_, dict):
            return {
                key: self._exclude_fields(value, exclude_keys=exclude_keys)
                for key, value in obj_.items()
                if key not in exclude_keys
            }
        elif isinstance(obj_, list):
            return [
                self._exclude_fields(item, exclude_keys=exclude_keys) for item in obj_
            ]
        else:
            return obj_
