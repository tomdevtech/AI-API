"""
This file provides the AI manager.

This module defines the `AIManager` class, which facilitates
model generation and availability checks.
"""

import unittest
import subprocess  # nosec B404
import requests


class AIManager:
    """AI manager class for basic management of the model."""

    def __init__(
        self,
        ModelName,
    ):
        """
        Initialize the AI manager with the given parameters.

        Args:
            ModelName (str): The name of the AI model to use.
        """
        self.ModelName = ModelName

    def CheckIfModelAvailability(self):
        """Check if the specified model exists and pull if necessary."""
        try:
            Result = subprocess.run(
                ["ollama", "list"],
                shell=True,
                capture_output=True,
                text=True,
                encoding="utf-8"
            )  # nosec

            if self.ModelName not in Result.stdout:
                print(f"Model '{self.ModelName}' not found. Downloading...")
                subprocess.run(
                    ["ollama", "pull", self.ModelName],
                    shell=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8"
                )  # nosec
                print(f"Model '{self.ModelName}' downloaded successfully.")
            else:
                print(f"Model '{self.ModelName}' already exists.")
        except Exception as E:
            print(f"Failed to check/download model '{self.ModelName}': {E}")
            exit(1)

    def CheckModelStatus(self):
        """Check if AI server is running."""
        try:
            Response = requests.get("http://localhost:11434/health", timeout=5)
            if Response.status_code == 200:
                print("Ollama server is running.")
            else:
                raise requests.exceptions.ConnectionError
        except requests.exceptions.ConnectionError:
            print("Ollama server not running. Attempting to start...")
            try:
                subprocess.Popen(
                    ["ollama", "stop"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    shell=True,
                    text=True,
                    encoding="utf-8"
                )  # nosec
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    shell=True,
                    text=True,
                    encoding="utf-8"
                )  # nosec
                print("Ollama server started successfully.")
            except Exception as E:
                print(f"Failed to start Ollama server: {E}")
                exit(1)

    @unittest.skip("Not needed for test.")
    def ManageAI(self):
        """
        Manage Ollama server and model availability.

        Ensures the Ollama server is running and the required model
        is available. If the server is not running, it attempts to start it.
        If the model is not available, it downloads the specified model.
        """
        self.CheckIfModelAvailability()
        self.CheckModelStatus()
