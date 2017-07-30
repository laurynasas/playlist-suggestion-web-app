import json
import urllib2
from urllib2 import HTTPError

import httplib2
from apiclient.discovery import build
from oauth2client import client
from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    view_config
)

from application import db
from application.models.database import Song
from controllers.get_youtube_playlist import YoutubePlaylist, SpotifyPlaylist
from controllers.get_youtube_playlist import list_playlists_mine, create_playlists, playlist_items_list_by_playlist_id
from controllers.suggestions.get_suggestions import create_suggestion_list

# ---------------- SPOTIFY API -------------------------------------------------------

SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

CLIENT_SECRETS_SPOTIFY = "d1e31b8f48b24e15aaa7c211b9970e8b"
CLIENT_ID_SPOTIFY = "b774e3bf851646c1b02928ea75802587"
CLIENT_SIDE_URL = "http://localhost"
PORT = 8080
REDIRECT_URI = "{}:{}/spotify-callback".format(CLIENT_SIDE_URL, PORT)
SCOPE = "playlist-modify-public playlist-modify-private"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID_SPOTIFY
}

# -------------------------------------------------------------------------------------


# ---------------- YOUTUBE API -------------------------------------------------------
# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.

# The CLIENT_SECRETS_FILE_YOUTUBE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret
CLIENT_SECRETS_FILE_YOUTUBE = "/home/sensitive/client_secrets_youtube.json"
YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE_YOUTUBE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = "WARNING: Please configure OAuth 2.0"


# -------------------------------------------------------------------------------------


class ShowNavigationBar:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='about', renderer='about.jinja2')
    def about(self):
        return {}

    @view_config(route_name='contact', renderer='contact.jinja2')
    def contact(self):
        return {}

