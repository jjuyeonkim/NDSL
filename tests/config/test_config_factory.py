# 20251118: Adapted from Gemini response. Currently being reviewed and tested.

import pytest
from config_factory import ConfigFactory
from config_parsers import NmlParser, YamlParser

# Importing domain_configs triggers the @register_config decorator
# import domain_configs # TODO: Do I need to do this?
from grid.config import GridConfig


# Define the application mapping (Metadata)
APP_MAP = {"grid": "GridConfig"}


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
    # Create Mock File
    f = tmp_path / "test.yaml"
    f.write_text(
        "something:\n  gravity: 5.5\ngrid:\n  npx: 10\n  npy: 10"
    )  # TODO: Modify this?

    # Load File
    configs = factory.load_components(f, APP_MAP)

    # Verify
    assert isinstance(configs["grid"], GridConfig)
    assert configs["grid"].npx == 10


def test_namelist_loading(factory, tmp_path):
    f = tmp_path / "test.nml"
    f.write_text(
        "&physics\n gravity=20.0\n/\n&grid\n npx=2\n npy=2\n/"
    )  # TODO: Modify this?

    configs = factory.load_components(f, APP_MAP)

    assert configs["grid"].npx == 2
    assert configs["grid"].npy == 2
    assert configs["grid"].npz == 0
