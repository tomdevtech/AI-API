"""
This module provides an API to manage AI model interactions, including model creation,
chat sessions, and API key management using FastAPI and Ollama.
"""

from fastapi import FastAPI, HTTPException, Header, Query
from aimanager import AIManager
import ollama
import subprocess
import uvicorn
from dotenv import load_dotenv
import uuid


class ApiManager:
    """API Manager class for managing interactions with the AI model and
    API key validations."""

    def __init__(self):
        """Initialize the API with environment configurations and setup."""
        load_dotenv()
        self.ApiKeyCredits = {}
        self.DownloadedModels = set()
        self.AiManager = AIManager()
        self.App = FastAPI()

        # Generate initial API key & check if ollama server is running.
        self.InitialApiKey = self.GenerateInitialApiKey()
        self.AiManager.CheckModelStatus()

        # Register routes
        self.App.get("/")(self.Root)
        self.App.post("/generate")(self.Generate)
        self.App.post("/chat")(self.Chat)
        self.App.post("/version")(self.Version)
        self.App.post("/generate-key")(self.GenerateApiKey)
        self.App.post("/create")(self.Create)
        self.App.get("/tags")(self.Tags)
        self.App.post("/show")(self.Show)
        self.App.post("/copy")(self.Copy)
        self.App.delete("/delete")(self.Delete)
        self.App.post("/pull")(self.Pull)
        self.App.post("/push")(self.Push)
        self.App.post("/embed")(self.Embed)
        self.App.post("/ps")(self.Ps)

    def Root(self):
        """Root endpoint to confirm API is running."""
        return {"message": "API is running!", "initial_api_key": self.InitialApiKey}

    def GenerateInitialApiKey(self):
        """Generate the initial API key on startup."""
        apiKey = str(uuid.uuid4())
        self.ApiKeyCredits[apiKey] = 5
        return apiKey

    def GenerateApiKey(self):
        """Generate a new API key and assign initial credits if the previous key has 0 credits."""
        if any(credits > 0 for credits in self.ApiKeyCredits.values()):
            raise HTTPException(
                status_code=401, detail="API Key creation not necessary."
            )
        apiKey = str(uuid.uuid4())
        self.ApiKeyCredits[apiKey] = 5
        return {"api_key": apiKey}

    def VerifyApiKey(
        self, xApiKey: str = Header(..., description="API Key for authorization")
    ):
        """Verify if the API key is valid and has sufficient credits."""
        if xApiKey not in self.ApiKeyCredits:
            raise HTTPException(status_code=401, detail="API Key not found.")
        if self.ApiKeyCredits[xApiKey] <= 0:
            raise HTTPException(
                status_code=401,
                detail="No credits left. Please generate a new API key.",
            )
        return xApiKey

    def DecrementCredits(self, xApiKey: str):
        """Decrement the credit count for a valid API key."""
        self.ApiKeyCredits[xApiKey] -= 1

    def HandleOllamaResponse(self, func, *args, **kwargs):
        """Generic handler for executing Ollama functions with error handling."""
        try:
            self.AiManager.CheckModelStatus()
            return func(*args, **kwargs)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def Generate(
        self,
        Prompt: str = Query(...),
        Model: str = Query(...),
        XApiKey: str = Header(...),
    ):
        """Generate a response from the AI model."""
        XApiKey = self.VerifyApiKey(XApiKey)
        self.DecrementCredits(XApiKey)
        self.AiManager.CheckIfModelAvailability(Model)
        return self.HandleOllamaResponse(
            ollama.chat,
            model=Model,
            messages=[{"role": "user", "content": Prompt}]
        )

    def Chat(
        self,
        Prompt: str = Query(...),
        Model: str = Query(...),
        XApiKey: str = Header(...),
    ):
        """Initiate a chat session with the AI model."""
        XApiKey = self.VerifyApiKey(XApiKey)
        self.DecrementCredits(XApiKey)
        self.AiManager.CheckIfModelAvailability(Model)
        return self.HandleOllamaResponse(
            ollama.chat,
            model=Model,
            messages=[{"role": "user", "content": Prompt}]
        )

    def Version(self, XApiKey: str = Header(...)):
        """Retrieve the current version of Ollama."""
        XApiKey = self.VerifyApiKey(XApiKey)
        self.DecrementCredits(XApiKey)
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            return {"version": result.stdout.strip()}
        except subprocess.CalledProcessError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve Ollama version: {str(e)}"
            )

    def Create(self, Model: str = Query(...), XApiKey: str = Header(...)):
        """Create a new model."""
        XApiKey = self.VerifyApiKey(XApiKey)
        self.DecrementCredits(XApiKey)
        return self.HandleOllamaResponse(ollama.create, model=Model)

    def Tags(self, XApiKey: str = Header(...)):
        """List all available model tags."""
        XApiKey = self.VerifyApiKey(XApiKey)
        self.DecrementCredits(XApiKey)
        return self.HandleOllamaResponse(ollama.list)

    def Show(self, Model: str = Query(...), XApiKey: str = Header(...)):
        """Show information about a specific model."""
        XApiKey = self.VerifyApiKey(XApiKey)
        self.DecrementCredits(XApiKey)
        return self.HandleOllamaResponse(ollama.show, model=Model)

    def Copy(
        self,
        SourceModel: str = Query(...),
        DestinationModel: str = Query(...),
        XApiKey: str = Header(...),
    ):
        """Copy an existing model to a new destination."""
        XApiKey = self.VerifyApiKey(XApiKey)
        self.DecrementCredits(XApiKey)
        return self.HandleOllamaResponse(
            ollama.copy,
            sourceModel=SourceModel,
            destinationModel=DestinationModel
        )

    def Delete(self, Model: str = Query(...), XApiKey: str = Header(...)):
        """Delete a model."""
        XApiKey = self.VerifyApiKey(XApiKey)
        self.DecrementCredits(XApiKey)
        return self.HandleOllamaResponse(ollama.delete, model=Model)

    def Pull(self, Model: str = Query(...), XApiKey: str = Header(...)):
        """Pull the latest version of a model."""
        XApiKey = self.VerifyApiKey(XApiKey)
        self.DecrementCredits(XApiKey)
        return self.HandleOllamaResponse(ollama.pull, model=Model)

    def Push(self, Model: str = Query(...), XApiKey: str = Header(...)):
        """Push a model to the remote repository."""
        XApiKey = self.VerifyApiKey(XApiKey)
        self.DecrementCredits(XApiKey)
        return self.HandleOllamaResponse(ollama.push, model=Model)

    def Embed(
        self,
        Model: str = Query(...),
        Data: str = Query(...),
        XApiKey: str = Header(...),
    ):
        """Embed data into a model."""
        XApiKey = self.VerifyApiKey(XApiKey)
        self.DecrementCredits(XApiKey)
        return self.HandleOllamaResponse(ollama.embed, model=Model, data=Data)

    def Ps(self, XApiKey: str = Header(...)):
        """List running model processes."""
        XApiKey = self.VerifyApiKey(XApiKey)
        self.DecrementCredits(XApiKey)
        return self.HandleOllamaResponse(ollama.ps)

    def Run(self):
        """Run the FastAPI application using Uvicorn."""
        uvicorn.run(self.App, host="127.0.0.1", port=8001)
