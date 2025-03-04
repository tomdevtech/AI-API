"""
This file provides a basic API to interact with an AI model.
Collection: https://www.postman.com/postman-student-programs/ollama-api/
"""

from fastapi import FastAPI, Depends, HTTPException, Header
import ollama
import os
from dotenv import load_dotenv


class APIManager:
    
    def __init__(self):
        """Initialize the api."""
        load_dotenv()
        self.API_KEY_CREDITS = {os.getenv("API_KEY"): 5}
        print(self.API_KEY_CREDITS)
        self.app = FastAPI()

    def verify_api_key(self, x_api_key: str = Header(None)):
        self.credits = self.API_KEY_CREDITS.get(x_api_key, 0)
        if self.credits <= 0:
            raise HTTPException(
                status_code=401, detail="Invalid API Key, or no credits"
            )

        return x_api_key

    @app.post("/generate")
    def generate(self, prompt: str, x_api_key: str = Depends(verify_api_key)):
        self.API_KEY_CREDITS[x_api_key] -= 1
        response = ollama.chat(
            model="mistral", messages=[{"role": "user", "content": prompt}]
        )
        return {"response": response["message"]["content"]}
    
    @app.post("/create")
    def create(self):
        print("Success!")

    @app.get("/tags")
    def tags(self, Permission):
        if Permission == True:
            print("Success!")

    @app.post("/show")
    def show(self):
        print("Success!")

    @app.post("/copy")
    def copy(self):
        print("Success!")
    
    @app.delete("/delete")
    def delete(self):
        print("Success!")

    @app.post("/pull")
    def pull(self):
        print("Success!")

    @app.post("/push")
    def push(self):
        print("Success!")

    @app.post("/embed")
    def embed(self):
        print("Success!")

    @app.post("/ps")
    def ps(self):
        print("Success!")

    @app.post("/chat")
    def chat(self):
        print("Success!")

    @app.post("/version")
    def version(self):
        print("Success!")
