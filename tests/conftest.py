import pytest


@pytest.fixture
def toml_file(shared_datadir):
    return shared_datadir / "pyproject.toml"
