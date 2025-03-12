"""
Basic tests to ensure the AuthService class is not empty and can be instantiated.
"""

from authservices import AuthService

def test_auth_service_instantiation():
    """Test that AuthService can be instantiated."""
    service = AuthService(
        Password="testpassword",
        Username="test",
        Email="test@example.com",
        FullName="Test User",
        Disabled=False,
        Algorithm="HS256",
        AccessTokenExpireMinutes=30
    )
    assert service is not None
    assert hasattr(service, 'App')
