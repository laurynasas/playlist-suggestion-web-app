import httplib2
from apiclient.discovery import build
from oauth2client import client
from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    view_config
)

from controllers.get_youtube_playlist import YoutubePlaylist
from controllers.get_youtube_playlist import list_playlists_mine, create_playlists

# ---------------- YOUTUBE API -------------------------------------------------------
# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.

# The CLIENT_SECRETS_FILE_YOUTUBE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"


# -------------------------------------------------------------------------------------


class TutorialViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='select_playlist', renderer='all_playlists.jinja2')
    def select_youtube_playlist(self):

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
