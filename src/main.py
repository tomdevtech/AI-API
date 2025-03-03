"""This file runs the model manager and the API."""

from api import APIManager
from aimanager import AIManager

class MainApp:
    """Main Application class to combine AI Assistant and UI."""

    def __init__(self,model_name):
        """Initialize the application."""
        self.AIManager = AIManager(model_name)

    def Run(self):
        """Run the application."""
        print("Managing Model...")
        self.AIManager.ManageAI()
        self.APIManager = APIManager()


if __name__ == "__main__":
        MainApp = MainApp("llama3.1:8b")
        MainApp.Run()
