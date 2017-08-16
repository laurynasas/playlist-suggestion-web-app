import base64
import json
import urllib
import urllib2
import warnings

from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    view_config
)

# ---------------- SPOTIFY API -------------------------------------------------------

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

CLIENT_SECRETS_SPOTIFY = "d1e31b8f48b24e15aaa7c211b9970e8b"
CLIENT_ID_SPOTIFY = "b774e3bf851646c1b02928ea75802587"
CLIENT_SIDE_URL = "http://playgen.eu-west-2.elasticbeanstalk.com"
PORT = 8080
REDIRECT_URI = "{}:{}/spotify-callback".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-private"

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    "client_id": CLIENT_ID_SPOTIFY
}


# -------------------------------------------------------------------------------------

class SpotifyAuthorize:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='spotify_auth')
    def authorize_spotify(self):
        self.request.session['oauth_redirect'] = 'select_spotify_playlist'
        return HTTPFound(location=self.request.route_url('spotify_redirect'))

    @view_config(route_name='spotify_redirect')
    def redirect_spotify(self):
        url_args = "&".join(["{}={}".format(key, urllib.quote(val)) for key, val in auth_query_parameters.iteritems()])
        auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
        return HTTPFound(location=auth_url)

    @view_config(route_name='spotify_callback')
    def spotify_callback(self):
        auth_token = self.request.GET.get('code')
        if not auth_token:
            warnings.warn("Spotify authorization failed with message: " + self.request.GET.get('error'))
            return HTTPFound(location=self.request.route_url('home'))

        code_payload = {
            "grant_type": "authorization_code",
            "code": str(auth_token),
            "redirect_uri": REDIRECT_URI
        }
        encoded_code_payload = urllib.urlencode(code_payload)
        base64encoded = base64.b64encode("{}:{}".format(CLIENT_ID_SPOTIFY, CLIENT_SECRETS_SPOTIFY))
        spotify_auth_headers = {"Authorization": "Basic {}".format(base64encoded)}

        post_request = urllib2.Request(SPOTIFY_TOKEN_URL, data=encoded_code_payload, headers=spotify_auth_headers)
        response = urllib2.urlopen(post_request)
        response_data = json.loads(response.read())

        self.request.session["spotify_token"] = response_data["access_token"]
        self.request.session["spotify_refresh_token"] = response_data["refresh_token"]

        redirect_url = self.request.session['oauth_redirect']
        return HTTPFound(location=self.request.route_url(redirect_url))

    @view_config(route_name='refresh_spotify_token')
    def refresh_spotify_token(self):
        code_payload = {
            "grant_type": "refresh_token",
            "refresh_token": self.request.session.get('spotify_refresh_token')
        }
        encoded_code_payload = urllib.urlencode(code_payload)

        base64encoded = base64.b64encode("{}:{}".format(CLIENT_ID_SPOTIFY, CLIENT_SECRETS_SPOTIFY))
        spotify_auth_headers = {"Authorization": "Basic {}".format(base64encoded)}

        post_request = urllib2.Request(SPOTIFY_TOKEN_URL, data=encoded_code_payload, headers=spotify_auth_headers)
        response = urllib2.urlopen(post_request)
        response_data = json.loads(response.read())

        # New tokens are Returned to Application
        self.request.session["spotify_token"] = response_data["access_token"]
        self.request.session["spotify_refresh_token"] = response_data["refresh_token"]

        redirect_url = self.request.session['oauth_redirect']
        return HTTPFound(location=self.request.route_url(redirect_url))
