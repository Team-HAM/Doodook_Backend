# utils.py

from rest_framework_simplejwt.tokens import RefreshToken

def create_jwt_token(user):
    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token
    return str(access_token)
