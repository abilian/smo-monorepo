from dataclasses import dataclass


@dataclass(frozen=True)
class CoreConfig:
    _data: dict

    def get(self, *path: list[str], default=None):
        """
        Retrieves a value from the configuration data using a list of keys.

        Args:
            path (list[str]): A list of keys to traverse the nested dictionary.
            default: The value to return if the key path is not found.
        Returns:
            The requested value, or the default if not found.
        """
        value = self._data
        try:
            for key in path:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
