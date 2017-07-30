import json
import urllib2
from urllib2 import HTTPError

from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    view_config
)

from controllers.get_youtube_playlist import SpotifyPlaylist
from controllers.get_youtube_playlist import create_playlists

# ---------------- SPOTIFY API -------------------------------------------------------

SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)


# -------------------------------------------------------------------------------------

class SpotifyImportPlaylist:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='select_spotify_playlist', renderer='all_playlists.jinja2')
    def select_spotify_playlist(self):
        authorization_header = {"Authorization": "Bearer {}".format(self.request.session.get('spotify_token'))}

        # Get profile data
        user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
        profile_request = urllib2.Request(user_profile_api_endpoint, headers=authorization_header)

        try:
            profile_response = urllib2.urlopen(profile_request)
        except HTTPError:
            print HTTPError
            return HTTPFound(location=self.request.route_url('refresh_spotify_token'))

        spotify_profile_data = json.loads(profile_response.read())

        # Get user playlists
        spotify_profile_url = spotify_profile_data["href"]
        playlist_api_endpoint = "{}/playlists".format(spotify_profile_url)
        playlists_request = urllib2.Request(playlist_api_endpoint, headers=authorization_header)

        try:
            playlists_response = urllib2.urlopen(playlists_request)
        except HTTPError:
            print HTTPError
            return HTTPFound(location=self.request.route_url('refresh_spotify_token'))

        playlist_data = json.loads(playlists_response.read())

        # Combine profile and playlist data to display
        playlists_iter = playlist_data
        playlists_instances = create_playlists(SpotifyPlaylist, playlists_iter)

        return {'playlists': playlists_instances, 'api': 'spotify'}
