"""SatNOGS DB Auth0 login module auth backend"""
import requests
from jose import jwt
from social_core.backends.oauth import BaseOAuth2


class Auth0(BaseOAuth2):
    """Auth0 OAuth authentication backend"""
    name = 'auth0'
    SCOPE_SEPARATOR = ' '
    ACCESS_TOKEN_METHOD = 'POST'
    REDIRECT_STATE = False
    EXTRA_DATA = [('email', 'email')]

    def authorization_url(self):
        """Return the authorization endpoint."""
        return "https://" + self.setting('DOMAIN') + "/authorize"

    def access_token_url(self):
        """Return the token endpoint."""
        return "https://" + self.setting('DOMAIN') + "/oauth/token"

    def auth_html(self):
        """Return the login endpoint."""
        return "https://" + self.setting('DOMAIN') + "/login/auth0"

    def get_user_id(self, details, response):
        """Return current user id."""
        return details['user_id']

    def get_user_details(self, response):
        # Obtain JWT and the keys to validate the signature
        id_token = response.get('id_token')
        jwks = requests.get('https://' + self.setting('DOMAIN') + '/.well-known/jwks.json')
        issuer = 'https://' + self.setting('DOMAIN') + '/'
        audience = self.setting('KEY')  # CLIENT_ID
        payload = jwt.decode(
            id_token, jwks.json(), algorithms=['RS256'], audience=audience, issuer=issuer
        )

        return {
            'username': payload['nickname'],
            # 'first_name': payload['name'],
            # 'picture': payload['picture'],
            'user_id': payload['sub'],
            'email': payload['email']
        }
