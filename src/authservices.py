"""This file provides a basic authentification methods."""

import secrets

class AuthServices:
    
    def __init__(self):
        self.Token = secrets.token_hex(20)
        self.TokenDict = {}