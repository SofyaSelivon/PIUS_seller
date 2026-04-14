from app.database.base import Base


def test_base_exists():
    assert Base is not None


def test_base_has_metadata():
    assert hasattr(Base, "metadata")


def test_base_is_declarative():
    assert hasattr(Base, "registry")
