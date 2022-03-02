"""
Pytest fixture to define char_maps for global use.
"""

import pytest


@pytest.fixture()
def char_maps():
    from src.debug_tokenize import char_maps
    return char_maps
