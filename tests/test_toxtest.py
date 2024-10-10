"""Minimal test for testing test-runner"""

from toxtest import __version__


def test_version() -> None:
    """Test the version string"""
    assert __version__ == "0.2.0"
