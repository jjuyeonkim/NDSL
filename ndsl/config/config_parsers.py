# 20251118: Adapted from Gemini response. Currently being reviewed and tested.

from pathlib import Path
from typing import Any

import f90nml
import yaml
from config_factory import ConfigParser


# TODO Note to self, this isn't ideal right now because we expect the structure of the namelists
# and YAML files to be different.


class NamelistParser(ConfigParser):
    """General Parser for Fortran Namelists."""

    def parse(self, filepath: Path) -> dict[str, Any]:
        # f90nml returns a dict-like object; convert to standard dict
        return f90nml.read(filepath).to_dict()


class YamlParser(ConfigParser):
    """General Parser for YAML files."""

    def parse(self, filepath: Path) -> dict[str, Any]:
        with filepath.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise TypeError(f"YAML content in {filepath} must be a dictionary.")
        return data
