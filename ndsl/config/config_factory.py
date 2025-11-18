# 20251118: Adapted from Gemini response. Currently being reviewed and tested.

import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, TypeVar


# TODO Why is this T necessary?
T = TypeVar("T", bound="Config")


# TODO Why is the kw_only=True needed?
@dataclass(kw_only=True)
class Config:
    """
    Base dataclass for all configurations.
    Includes a helper to safely load from dicts, ignoring extra keys.
    """

    @classmethod
    def from_dict(cls: type[T], data: dict[str, Any]) -> T:
        """
        Creates an instance of the dataclass, filtering out any keys
        in 'data' that aren't fields in the dataclass.
        """
        # TODO: Maybe this can be overrided to use dacite in Config classes that inherit from it.

        # In general, inspect the dataclass fields to know what acts as valid input
        valid_keys = inspect.signature(
            cls
        ).parameters  # TODO: Do we have to use inspect here?
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)


# TODO Why is the config registry global?
_CONFIG_REGISTRY: dict[str, type[Config]] = {}


# TODO Why is the Callable with type T needed?
def register_config(name: str) -> Callable[[type[T]], type[T]]:
    """Decorator to register a Config subclass."""

    def decorator(cls: type[T]) -> type[T]:
        _CONFIG_REGISTRY[name] = cls
        return cls

    return decorator


# Examples that will inherit from ConfigParser: YamlConfigParser, NmlConfigParser
class ConfigParser(ABC):
    @abstractmethod
    def parse(self, filepath: Path) -> dict[str, Any]:
        """Parses file and returns a dict"""
        pass


class ConfigFactory:
    def __init__(self) -> None:
        self._parsers: dict[str, ConfigParser] = {}

    def register_parser(self, extension: str, parser: ConfigParser) -> None:
        """Registers a parser for a specific file extension."""
        self._parsers[extension.lower()] = parser

    def load_components(
        self,
        filepath: Path,
        app_map: dict[
            str, str
        ],  # TODO : This might need some modifying. Maybe instead of a 1:1 mapping, we'll need one to many mapping?
    ) -> dict[str, Config]:
        """
        Loads a configuration from a file.
        """
        if not filepath.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")

        # Locate Parser
        ext = filepath.suffix.lower()
        if parser := self._parsers.get(
            ext
        ):  # Python 3.8+ Walrus operator # TODO What is Walrus?
            data = parser.parse(filepath)
        else:
            raise ValueError(f"No parser registered for extension: '{ext}'")

        results: dict[str, Config] = {}

        # TODO: What is the comp_name?
        for comp_name, params in data.items():
            # Identify the class name from the map
            if not (
                config_type_name := app_map.get(comp_name)
            ):  # TODO: Not sure if this is going to be the same in our case. Maybe a 1:many map where multiple comp_names can be associated with a single config_type_name? Maybe we gather all of the related ones? I think the keys
                raise ValueError(f"Component '{comp_name}' not found.")

            # Fetch the class from the registry
            if not (config_class := _CONFIG_REGISTRY.get(config_type_name)):
                raise ValueError(f"Config class '{config_type_name}' not registered.")

            # Create instance using the safe from_dict builder
            # TODO What's meant by "safe"
            results[comp_name] = config_class.from_dict(params)

        return results
