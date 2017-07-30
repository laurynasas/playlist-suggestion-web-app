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

from controllers.get_youtube_playlist import YoutubePlaylist, SpotifyPlaylist
from controllers.get_youtube_playlist import playlist_items_list_by_playlist_id

# ---------------- SPOTIFY API -------------------------------------------------------

xSPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# -------------------------------------------------------------------------------------


# ---------------- YOUTUBE API -------------------------------------------------------
# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.

# The CLIENT_SECRETS_FILE_YOUTUBE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"


# -------------------------------------------------------------------------------------


class CreatePlaylist:
    def __init__(self, request):
        self.request = request

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

            try:
                profile_response = urllib2.urlopen(profile_request)
            except HTTPError:
                print HTTPError
                return HTTPFound(location=self.request.route_url('refresh_spotify_token'))

            spotify_profile_data = json.loads(profile_response.read())

            # Get user playlists
            spotify_profile_url = spotify_profile_data["href"]

            playlist_tracks_endpoint = "{}/playlists/{}/tracks".format(spotify_profile_url, playlist_id)
            selected_playlist_tracks_req = urllib2.Request(playlist_tracks_endpoint, headers=authorization_header)

            try:
                selected_playlist_tracks_response = urllib2.urlopen(selected_playlist_tracks_req)
            except HTTPError:
                print HTTPError
                return HTTPFound(location=self.request.route_url('refresh_spotify_token'))
            tracks = json.loads(selected_playlist_tracks_response.read())

            playlist_songs = SpotifyPlaylist.get_playlist_songs(tracks)

            return {'playlist': playlist_songs, 'playlist_id': playlist_id,
                    'playlist_string': json.dumps(playlist_songs)}
        else:
            return {}
