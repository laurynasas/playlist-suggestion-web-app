import base64
import json
import urllib
import urllib2
import warnings

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


class TutorialViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='select_playlist', renderer='all_playlists.jinja2')
    def index(self):

        if 'credentials' not in self.request.session:
            return HTTPFound(location=self.request.route_url('redirect'))
        credentials = client.OAuth2Credentials.from_json(self.request.session['credentials'])
        if credentials.access_token_expired:
            return HTTPFound(location=self.request.route_url('redirect'))
        else:
            http_auth = credentials.authorize(httplib2.Http())
            service = build(API_SERVICE_NAME, API_VERSION,
                            http=http_auth)

            playlists_info = list_playlists_mine(service,
                                                 part='snippet,contentDetails',
                                                 mine=True)

            playlists_instances = create_playlists(YoutubePlaylist, playlists_info)

            return {'playlists': playlists_instances, 'api': 'youtube'}

    @view_config(route_name='select_spotify_playlist', renderer='all_playlists.jinja2')
    def select_spotify_playlist(self):

        # Auth Step 6: Use the access token to access Spotify API
        authorization_header = {"Authorization": "Bearer {}".format(self.request.session.get('spotify_token'))}

        # Get profile data
        user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
        profile_request = urllib2.Request(user_profile_api_endpoint, headers=authorization_header)
        profile_response = urllib2.urlopen(profile_request)
        spotify_profile_data = json.loads(profile_response.read())

        if profile_response.code != 200:
            return HTTPFound(location=self.request.route_url('refresh_spotify_token'))

        # Get user playlists
        spotify_profile_url = spotify_profile_data["href"]
        playlist_api_endpoint = "{}/playlists".format(spotify_profile_url)
        playlists_request = urllib2.Request(playlist_api_endpoint, headers=authorization_header)
        playlists_response = urllib2.urlopen(playlists_request)
        playlist_data = json.loads(playlists_response.read())

        if playlists_response.code != 200:
            return HTTPFound(location=self.request.route_url('refresh_spotify_token'))

        # Combine profile and playlist data to display
        playlists_iter = playlist_data
        playlists_instances = create_playlists(SpotifyPlaylist, playlists_iter)

        return {'playlists': playlists_instances, 'api': 'spotify'}

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

        return HTTPFound(location=self.request.route_url('select_spotify_playlist'))

    @view_config(route_name='home', renderer='playlist.jinja2')
    def show_songs(self):
        playlist_id = self.request.POST.get('playlist_id')
        api = self.request.POST.get('api')
        print "api", api
        if api == "youtube":
            if playlist_id:
                if 'credentials' not in self.request.session:
                    return HTTPFound(location=self.request.route_url('redirect'))
                credentials = client.OAuth2Credentials.from_json(self.request.session['credentials'])
                if credentials.access_token_expired:
                    return HTTPFound(location=self.request.route_url('redirect'))
                else:
                    http_auth = credentials.authorize(httplib2.Http())
                    service = build(API_SERVICE_NAME, API_VERSION,
                                    http=http_auth)
                    playlist_id = self.request.POST.get('playlist_id')
                    playlist_info = playlist_items_list_by_playlist_id(service,
                                                                       part='snippet,contentDetails',
                                                                       maxResults=25,
                                                                       playlistId=playlist_id)

                    playlist_songs = YoutubePlaylist.get_playlist_songs(playlist_info)

                    return {'playlist': playlist_songs, 'playlist_id': playlist_id,
                            'playlist_string': json.dumps(playlist_songs)}
        elif api == 'spotify':
            authorization_header = {"Authorization": "Bearer {}".format(self.request.session.get('spotify_token'))}
            user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
            profile_request = urllib2.Request(user_profile_api_endpoint, headers=authorization_header)
            profile_response = urllib2.urlopen(profile_request)
            spotify_profile_data = json.loads(profile_response.read())

            if profile_response.code != 200:
                return HTTPFound(location=self.request.route_url('refresh_spotify_token'))

            # Get user playlists
            spotify_profile_url = spotify_profile_data["href"]

            playlist_tracks_endpoint = "{}/playlists/{}/tracks".format(spotify_profile_url, playlist_id)
            selected_playlist_tracks_req = urllib2.Request(playlist_tracks_endpoint, headers=authorization_header)
            selected_playlist_tracks_response = urllib2.urlopen(selected_playlist_tracks_req)
            tracks = json.loads(selected_playlist_tracks_response.read())

            if selected_playlist_tracks_response.code != 200:
                return HTTPFound(location=self.request.route_url('refresh_spotify_token'))

            playlist_songs = SpotifyPlaylist.get_playlist_songs(tracks)

            return {'playlist': playlist_songs, 'playlist_id': playlist_id,
                    'playlist_string': json.dumps(playlist_songs)}
        else:
            return {}

    @view_config(route_name='results', renderer='results.jinja2')
    def results(self):
        print "results"

        user_playlist = self.request.POST.get('playlist')
        user_limit = int(self.request.POST.get('limit'))
        number_bands = int(self.request.POST.get('bands'))
        user_playlist = user_playlist.split(",")
        print "here", user_playlist
        result_list = create_suggestion_list(user_playlist, required_suggestions=user_limit,
                                             number_bands=number_bands)
        if result_list:
            result_list = [song for song, source in result_list]
        return {"result_playlist": result_list}

    @view_config(route_name='suggestions', renderer='json')
    def get_suggestions(self):

        all_songs = db.query(Song)
        titles = [song.title + " - " + song.artist_title for song in all_songs]
        return {'suggestions': titles}

    @view_config(route_name='about', renderer='about.jinja2')
    def about(self):
        return {}

    @view_config(route_name='contact', renderer='contact.jinja2')
    def contact(self):
        return {}

    @view_config(route_name='spotify_redirect')
    def redirect_spotify(self):
        url_args = "&".join(["{}={}".format(key, urllib.quote(val)) for key, val in auth_query_parameters.iteritems()])
        auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
        return HTTPFound(location=auth_url)

    @view_config(route_name='spotify_callback')
    def spotify_callback(self):

        # Auth Step 4: Requests refresh and access tokens
        auth_token = self.request.GET.get('code')
        if not auth_token:
            print self.request.GET.get('error')
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

        # Auth Step 5: Tokens are Returned to Application
        self.request.session["spotify_token"] = response_data["access_token"]
        self.request.session["spotify_refresh_token"] = response_data["refresh_token"]

        return HTTPFound(location=self.request.route_url('select_spotify_playlist'))

    @view_config(route_name='redirect')
    def oauth2callback(self):

        flow = client.flow_from_clientsecrets(
            CLIENT_SECRETS_FILE_YOUTUBE,
            scope=YOUTUBE_READ_WRITE_SSL_SCOPE,
            redirect_uri=self.request.route_url('redirect'))
        flow.params['include_granted_scopes'] = 'true'

        if 'code' not in self.request.GET:
            auth_uri = flow.step1_get_authorize_url()
            return HTTPFound(location=auth_uri)
        else:
            auth_code = self.request.GET.get('code')
            credentials = flow.step2_exchange(auth_code)
            self.request.session['credentials'] = credentials.to_json()

            return HTTPFound(location=self.request.route_url('select_playlist'))
