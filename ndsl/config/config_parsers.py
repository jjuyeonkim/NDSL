# 20251118: Adapted from Gemini response. Currently being reviewed and tested.

from pathlib import Path
from typing import Any

import yaml

from ndsl.config import ConfigParser
from ndsl.utils import f90nml_as_dict, load_f90nml


# TODO Note to self, this isn't ideal right now because we expect the structure of the namelists
# and YAML files to be different.


class NmlParser(ConfigParser):
    """General Parser for Fortran Namelists."""

    def parse(self, filepath: Path) -> dict[str, Any]:
        nml = load_f90nml(filepath)

        # TODO Allow the config_nml_map to be configurable
        config_nml_map = {
            "GridConfig": ["fv_core_nml"],
            "DynamicalCoreConfig": (
                "main_nml",
                "coupler_nml",
                "fv_core_nml",
            ),
            "PhysicsConfig": (
                "main_nml",
                "coupler_nml",
                "gfdl_cloud_microphysics_nml",
                "integ_phys_nml",
                "gfs_physics_nml",
            ),
        }

        # Restructure the dict based on the config_nml_map
        standardized_data = {}
        for config_name, target_groups in config_nml_map.items():
            standardized_data[config_name] = f90nml_as_dict(
                nml, flatten=True, target_groups=target_groups
            )
        return standardized_data


class YamlParser(ConfigParser):
    """General Parser for YAML files."""

    def parse(self, filepath: Path) -> dict[str, Any]:
        # TODO Allow the YAML_CONFIG_MAP to be configurable
        # TODO What to do with the yaml parameters that are hanging and not under some key?
        config_yaml_map = {
            "GridConfig": ("grid_config"),
            "DynamicalCoreConfig": ("dycore_config"),
            "PhysicsConfig": ("physics_config"),
        }
        with filepath.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise TypeError(f"YAML content in {filepath} must be a dictionary.")

        # Restructure the dict based on the config_yaml_map
        standardized_data = {}
        for config_name, yaml_key in config_yaml_map.items():
            if yaml_key in data.keys():
                standardized_data[config_name] = data[
                    yaml_key
                ]  # TODO do I need to do a deep copy?
            else:
                standardized_data[config_name] = {}  # Otherwise, pass in empty
        return standardized_data
