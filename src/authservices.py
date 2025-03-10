"""This file provides basic authentication methods using FastAPI, JWT, and password hashing."""

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import uvicorn

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
    """Model representing a user stored in the database with a hashed password."""
    HashedPassword: str

class AuthService:
    """Authentication services for creating tokens, verifying users, and managing authentication flow."""

    def __init__(self):
        """Initialize authentication service with default values."""
        self.SecretKey = "83daa0256a2289b0fb23693bf1f6034d44396675749244721a2b20e896e11662"
        self.Algorithm = "HS256"
        self.AccessTokenExpireMinutes = 30
        self.PwdContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.Oauth2Scheme = OAuth2PasswordBearer(tokenUrl="token")
        self.App = FastAPI()
        self.TestDb = {
            "test": UserInDB(
                Username="max",
                FullName="Max Mustermann",
                Email="MaxMuster@gmail.com",
                HashedPassword=self.PwdContext.hash("password"),
                Disabled=False
            )
        }

        @self.App.post("/token", response_model=Token)
        async def Login(formData: OAuth2PasswordRequestForm = Depends()):
            return await self.LoginForAccessToken(formData)

        @self.App.get("/users/me/", response_model=User)
        async def ReadUsersMe(CurrentUser: User = Depends(self.GetCurrentActiveUser)):
            return CurrentUser

    def VerifyPassword(self, PlainPassword, HashedPassword):
        return self.PwdContext.verify(PlainPassword, HashedPassword)

    def GetPasswordHash(self, Password):
        return self.PwdContext.hash(Password)

    def GetUser(self, Username: str):
        return self.TestDb.get(Username)

    def AuthenticateUser(self, Username: str, Password: str):
        User = self.GetUser(Username)
        if not User or not self.VerifyPassword(Password, User.HashedPassword):
            return None
        return User

    def CreateAccessToken(self, Data: dict, ExpiresDelta: timedelta | None = None):
        ToEncode = Data.copy()
        Expire = datetime.utcnow() + (ExpiresDelta or timedelta(minutes=15))
        ToEncode.update({"exp": Expire})
        return jwt.encode(ToEncode, self.SecretKey, algorithm=self.Algorithm)

    async def GetCurrentUser(self, Token: str = Depends()):
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
        if CurrentUser.Disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return CurrentUser

    async def LoginForAccessToken(self, FormData: OAuth2PasswordRequestForm = Depends()):
        User = self.AuthenticateUser(FormData.username, FormData.password)
        if not User:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        AccessTokenExpires = timedelta(minutes=self.AccessTokenExpireMinutes)
        AccessToken = self.CreateAccessToken(
            Data={"sub": User.Username}, ExpiresDelta=AccessTokenExpires
        )
        return {"AccessToken": AccessToken, "TokenType": "bearer"}

    def Run(self):
        """Run the API."""
        uvicorn.run(self.App, host="127.0.0.1", port=8000)
