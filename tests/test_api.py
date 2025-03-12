"""
Basic tests to ensure the ApiManager class is not empty and can be instantiated.
"""

from api import ApiManager

def test_api_manager_instantiation():
    """Test that ApiManager can be instantiated."""
    manager = ApiManager()
    assert manager is not None
    assert hasattr(manager, 'App')
