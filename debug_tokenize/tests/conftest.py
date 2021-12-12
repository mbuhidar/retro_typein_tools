"""
Pytest fixture to define char_maps for global use.
"""

import pytest


@pytest.fixture()
def char_maps():
    import char_maps
    return char_maps
