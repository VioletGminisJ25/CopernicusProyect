from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import os

load_dotenv()


class Auth:
    """
    Modulo de autenticacion para el acceso a la API de Copernicus Data Space Ecosystem (CDSE).
    Este modulo utiliza el flujo de credenciales de cliente para obtener un token de acceso.
    """

    def __init__(self):
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.token = self.get_token()

    def get_token(self):
        """Obtiene un token de acceso utilizando el flujo de credenciales de cliente."""
        client = BackendApplicationClient(client_id=self.client_id)
        self.oauth = OAuth2Session(client=client)
        token = self.oauth.fetch_token(
            token_url="https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
            client_secret=self.client_secret,
            include_client_id=True,
        )
        return token
