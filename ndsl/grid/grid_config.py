# 20251118: Partially adapted from Gemini response. Currently being reviewed and tested.

from __future__ import annotations

import dataclasses
from typing import Optional, Tuple

import f90nml
from ndsl.config import Config, register_config
from dacite import Config as DaciteConfig
from dacite import from_dict

from ndsl.utils import f90nml_as_dict


DEFAULT_INT = 0
DEFAULT_BOOL = False
DEFAULT_GRID_NML_GROUPS = ("fv_core_nml",)


@register_config("GridConfig")
@dataclasses.dataclass(kw_only=True)  # TODO: Is this necessary?
class GridConfig(Config):
    npx: int = DEFAULT_INT
    npy: int = DEFAULT_INT
    npz: int = DEFAULT_INT
    layout: Tuple[int, int] = (1, 1)
    target_nml_groups: Optional[Tuple[str, ...]] = DEFAULT_GRID_NML_GROUPS

    @classmethod
    def from_f90nml(
        cls,
        nml: f90nml.Namelist,
        target_groups: Tuple[str, ...] | None = DEFAULT_GRID_NML_GROUPS,
    ) -> GridConfig:
        """Uses the nml to create a GridConfig.

        Args:
            nml: f90nml.Namelist
            target_groups: Tuple[str,...] | None
                This list will be used to specify which groups in the nml to
                use when initializing the GridConfig. If None, all
                groups will be used. (Default: DEFAULT_GRID_NML_GROUPS)
        """
        # groups = list(target_groups) if target_groups is not None else None
        nml_dict = f90nml_as_dict(nml, flatten=True, target_groups=target_groups)
        nml_dict["target_nml_groups"] = target_groups
        return cls.from_dict(nml_dict)

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> GridConfig:
        """Create a GridConfig from the given data.

        Args:
            data: "flattened" dictionary where the keys match the class member variables
        """
        # NOTE: We're setting strict to False so that extra keys in the data are
        # ignored. Eventually, we'd like to turn this to True once we move away from
        # expecting dicts that are basically flattened f90nml files.

        dacite_config = DaciteConfig(
            strict=False,
            type_hooks={
                Tuple[int, int]: lambda x: tuple(x),
                Tuple[str, ...]: lambda x: tuple(x) if x is not None else None,
            },
        )
        return from_dict(data_class=GridConfig, data=data, config=dacite_config)
