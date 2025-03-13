"""
Basic tests to ensure the Main class is not empty and can be used.
"""

from main import MainApp


class TestMainApp:
    """Test suite for the MainApp class."""

    def test_instance_creation(self):
        """Test if MainApp instance is created successfully."""
        app_instance = MainApp()
        assert app_instance is not None
        assert isinstance(app_instance, MainApp)
