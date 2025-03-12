"""
This file provides basic authentication methods using FastAPI, JWT, and password hashing.
"""

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import uvicorn
import secrets
import bcrypt


class Token(BaseModel):
    """Model representing a JWT access token."""
    AccessToken: str
    TokenType: str


class TokenData(BaseModel):
    """Model for storing token data, specifically the username."""
    Username: str | None = None


class User(BaseModel):
    """Model representing a user."""
    Username: str
    Email: str | None = None
    FullName: str | None = None
    Disabled: bool | None = None


class UserInDB(User):
    """Model representing a user stored in the database with a
    hashed password."""
    HashedPassword: str


class AuthService:
    """Authentication services for creating tokens, verifying users,
    and managing authentication flow."""

    def __init__(
        self,
        Password,
        Username,
        Email,
        FullName,
        Disabled,
        Algorithm,
        AccessTokenExpireMinutes,
    ):
        """Initialize authentication service with default values."""
        self.Password = Password
        self.SecretKey = secrets.token_hex(32)
        self.Algorithm = Algorithm
        self.AccessTokenExpireMinutes = AccessTokenExpireMinutes
        self.Oauth2Scheme = OAuth2PasswordBearer(tokenUrl="token")
        self.App = FastAPI()
        self.TestDb = {
            "test": UserInDB(
                Username=Username,
                FullName=FullName,
                Email=Email,
                HashedPassword=self.GetPasswordHash(self.Password),
                Disabled=Disabled,
            )
        }

        self.App.post("/token", response_model=Token)(self.Login)
        self.App.get("/users/me/", response_model=User)(self.ReadUsersMe)
        self.App.get("/", tags=["Root"])(self.Root)

    async def Root(self):
        """Root endpoint for the API."""
        return {"message": "Authentication API is running."}

    def VerifyPassword(self, PlainPassword: str, HashedPassword: str):
        """Verify a plaintext password against its hashed version."""
        return bcrypt.checkpw(
            PlainPassword.encode("utf-8"), HashedPassword.encode("utf-8")
        )

    def GetPasswordHash(self, Password: str):
        """Hash a plaintext password using bcrypt."""
        return bcrypt.hashpw(
            Password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def GetUser(self, Username: str):
        """Retrieve a user from the in-memory database by username."""
        return self.TestDb.get(Username)

    def AuthenticateUser(self, Username: str, Password: str):
        """Authenticate a user by verifying their password."""
        User = self.GetUser(Username)
        if not User or not self.VerifyPassword(Password, User.HashedPassword):
            return None
        return User

    def CreateAccessToken(self, Data: dict, ExpiresDelta: timedelta | None = None):
        """Create a JWT access token with an expiration time."""
        ToEncode = Data.copy()
        Expire = datetime.now(timezone.utc) + (
            ExpiresDelta or timedelta(minutes=15)
        )
        ToEncode.update({"exp": Expire})
        return jwt.encode(ToEncode, self.SecretKey, algorithm=self.Algorithm)

    async def Login(self, FormData: OAuth2PasswordRequestForm = Depends()):
        """Login endpoint to generate an access token."""
        return await self.LoginForAccessToken(FormData)

    async def ReadUsersMe(self, CurrentUser: User = Depends()):
        """Retrieve information about the current authenticated user."""
        return await self.GetCurrentActiveUser(CurrentUser)

    async def GetCurrentUser(self, Token: str = Depends()):
        """Retrieve the current user based on the provided JWT token."""
        CredentialsException = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            Payload = jwt.decode(Token, self.SecretKey, algorithms=[self.Algorithm])
            Username: str = Payload.get("sub")
            if Username is None:
                raise CredentialsException
        except JWTError:
            raise CredentialsException
        User = self.GetUser(Username)
        if User is None:
            raise CredentialsException
        return User

    async def GetCurrentActiveUser(self, CurrentUser: User = Depends()):
        """Ensure that the current user is active and not disabled."""
        if CurrentUser.Disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return CurrentUser

    async def LoginForAccessToken(
        self, FormData: OAuth2PasswordRequestForm = Depends()
    ):
        """Generate a JWT token for the authenticated user."""
        User = self.AuthenticateUser(FormData.username, FormData.password)
        if not User:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        AccessTokenExpires = timedelta(minutes=self.AccessTokenExpireMinutes)
        AccessToken = self.CreateAccessToken(
            Data={"sub": User.Username},
            ExpiresDelta=AccessTokenExpires
        )
        return {"AccessToken": AccessToken, "TokenType": "bearer"}

    def Run(self):
        """Start the FastAPI application using uvicorn."""
        uvicorn.run(self.App, host="127.0.0.1", port=8000)
