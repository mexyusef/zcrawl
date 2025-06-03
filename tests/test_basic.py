"""
Basic tests for ZCrawl.
"""

import pytest


def test_import():
    """Test that the package can be imported."""
    import zcrawl
    assert zcrawl is not None


def test_version():
    """Test that the package has a version."""
    import zcrawl
    assert hasattr(zcrawl, "__version__")
