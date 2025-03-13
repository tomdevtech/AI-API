"""Main module integrating authentication and AI API services."""

from authservices import AuthService
from api import ApiManager
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


class MainApp:
    """Main application class integrating authentication
    and AI API services."""

    def __init__(self):
        """Initialize the MainApp with authentication and API managers."""
        self.AuthService = AuthService(
            Password="your_password",
            Username="your_username",
            Email="your_email@example.com",
            FullName="Your Full Name",
            Disabled=False,
            Algorithm="HS256",
            AccessTokenExpireMinutes=30,
        )

        self.ApiManager = ApiManager()
        self.App = FastAPI()

        # Include authentication and API routes
        self.App.include_router(self.AuthService.App.router)
        self.App.include_router(self.ApiManager.App.router)

        self.OAuth2Scheme = OAuth2PasswordBearer(tokenUrl="/login")

        # Register API endpoints
        self.RegisterRoutes()

    def RegisterRoutes(self):
        """Register API endpoints for the FastAPI application."""

        @self.App.get("/")
        def Root():
            """Root endpoint to confirm the API is running."""
            return {"message": "Main API is running with authentication."}

        @self.App.post("/login")
        async def Login(FormData: OAuth2PasswordRequestForm = Depends()):
            """Endpoint for user login and JWT token generation.

            Args:
                FormData (OAuth2PasswordRequestForm): User login data.

            Returns:
                dict: JWT token with token type.
            """
            return await self.AuthService.LoginForAccessToken(FormData)

        @self.App.post("/secure-chat")
        async def SecureChat(Prompt: str, Model: str,
                             User=Depends(self.VerifyToken)):
            """Protected endpoint to interact with the AI model.

            Args:
                Prompt (str): User prompt for the AI model.
                Model (str): Name of the AI model to use.
                User (User): Authenticated user from token verification.

            Returns:
                dict: AI model response.
            """
            ApiKey = self.ApiManager.GenerateInitialApiKey()
            return self.ApiManager.Chat(Prompt=Prompt,
                                        Model=Model, XApiKey=ApiKey)

    async def VerifyToken(
        self, Token: str = Depends(OAuth2PasswordBearer(tokenUrl="/login"))
    ):
        """Verify the provided JWT token and return the authenticated user.

        Args:
            Token (str): JWT token to verify.

        Raises:
            HTTPException: If the token is invalid or the
            user cannot be verified.

        Returns:
            User: The authenticated user.
        """
        try:
            User = await self.AuthService.GetCurrentUser(Token)
            return User
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def Run(self):
        """Run the FastAPI application using Uvicorn."""
        uvicorn.run(self.App, host="127.0.0.1", port=8002)


if __name__ == "__main__":
    MainAppInstance = MainApp()
    MainAppInstance.Run()
