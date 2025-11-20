# 20251118: Adapted from Gemini response. Currently being reviewed and tested.

import pytest
from ndsl.config import ConfigFactory
from ndsl.config import NmlParser, YamlParser

# Importing domain_configs triggers the @register_config decorator
# import domain_configs # TODO: Do I need to do this?
from ndsl.grid import GridConfig
from ndsl.utils import DEFAULT_GRID_NML_GROUPS
from pyfv3._config import DEFAULT_DYCORE_NML_GROUPS, DynamicalCoreConfig
from pyshield._config import DEFAULT_PHYS_NML_GROUPS, PhysicsConfig


# Define the application mapping (Metadata)
#APP_MAP = {"grid": (DEFAULT_GRID_NML_GROUPS, "GridConfig")}

# TODO: Would this work? Straight-forward for yaml
YAML_CONFIG_MAP = {
    "GridConfig": ("grid_config"),
    "DynamicalCoreConfig": ("dycore_config"),
    "PhysicsConfig": ("physics_config")
}

# TODO: Does this help me? This could be passed into the NmlParser and used?
# This wold be used to pull out certain sections and flatten the nml to eventually be passed into constructors
# Each of the parsers would take this and try to use it accordingly to create the appropriate dict version of the 
NML_CONFIG_MAP = {
    "GridConfig": DEFAULT_GRID_NML_GROUPS, 
    # ["fv_core_nml"]

    "DynamicalCoreConfig": DEFAULT_DYCORE_NML_GROUPS,
    #(
    #    "main_nml",
    #    "coupler_nml",
    #    "fv_core_nml",
    #)

    "PhysicsConfig": DEFAULT_PHYS_NML_GROUPS,
    #(
    #    "main_nml",
    #    "coupler_nml",
    #    "gfdl_cloud_microphysics_nml",
    #    "integ_phys_nml",
    #    "gfs_physics_nml",
    #)
}

@pytest.fixture
def factory():
    f = ConfigFactory()
    f.register_parser(".yaml", YamlParser())
    f.register_parser(".nml", NmlParser())
    return f


def test_dataclass_creation():
    """Test that our dataclasses work as expected."""
    conf = GridConfig(npx=10)
    assert conf.npx == 10
    assert conf.npy == 0  # Default
    assert conf.layout == (1, 1)


def test_extra_field_filtering():
    """Test that Config.from_dict ignores unknown keys."""
    data = {"npx": 10, "npy": 10, "UNKNOWN_KEY": 999}
    # This would crash a normal dataclass, but from_dict handles it
    conf = GridConfig.from_dict(data)
    assert conf.npx == 10
    assert conf.npy == 10
    assert conf.npz == 0


def test_yaml_loading(factory, tmp_path):
    f = tmp_path / "test.yaml"
    f.write_text(
        #"something:\n  gravity: 5.5\ngrid_config:\n  npx: 10\n  npy: 10"
        "grid_config:\n  npx: 10\n  npy: 10"
    )  # TODO: Modify this?

    # Load File
    configs = factory.load_components(f, ["GridConfig"])

    # Verify
    assert isinstance(configs["GridConfig"], GridConfig)
    assert configs["GridConfig"].npx == 10


def test_namelist_loading(factory, tmp_path):
    f = tmp_path / "test.nml"
    f.write_text(
        #"&physics\n gravity=20.0\n/\n&grid\n npx=2\n npy=2\n/"
        "&fv_core_nml\n npx=2\n npy=2\n/"
    )  # TODO: Modify this?

    configs = factory.load_components(f, ["GridConfig"])

    assert configs["GridConfig"].npx == 2
    assert configs["GridConfig"].npy == 2
    assert configs["GridConfig"].npz == 0
