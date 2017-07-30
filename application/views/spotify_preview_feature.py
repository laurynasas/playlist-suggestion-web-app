import base64
import json
import urllib
import urllib2

from pyramid.view import (
    view_config
)

# ---------------- SPOTIFY API -------------------------------------------------------

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

CLIENT_SECRETS_SPOTIFY = "d1e31b8f48b24e15aaa7c211b9970e8b"
CLIENT_ID_SPOTIFY = "b774e3bf851646c1b02928ea75802587"


# -------------------------------------------------------------------------------------


class SpotifyPreviewTrack:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='get_preview_url', renderer='json')
    def get_preview_url(self):
        song_title = self.request.GET.get('title')
        song_title = song_title.replace("by", "-")
        token = self.request.session.get('spotify_token')
        code_payload = {
            "grant_type": "client_credentials",
        }

        encoded_code_payload = urllib.urlencode(code_payload)
        base64encoded = base64.b64encode("{}:{}".format(CLIENT_ID_SPOTIFY, CLIENT_SECRETS_SPOTIFY))
        spotify_auth_headers = {"Authorization": "Basic {}".format(base64encoded)}

        if not token:
            self.request.session['oauth_redirect'] = 'get_preview_url'

            post_request = urllib2.Request(SPOTIFY_TOKEN_URL, data=encoded_code_payload, headers=spotify_auth_headers)
            response = urllib2.urlopen(post_request)
            response_data = json.loads(response.read())

            self.request.session["spotify_token"] = response_data["access_token"]

        code_payload = {
            "q": song_title,
            "type": "track",
            "limit": "1"
        }

        authorization_header = {"Authorization": "Bearer {}".format(self.request.session.get('spotify_token'))}
        url_args = "&".join(["{}={}".format(key.encode("utf-8"), urllib.quote(val.encode("utf-8"))) for key, val in code_payload.iteritems()])
        search_url = "{}/search?{}".format(SPOTIFY_API_URL, url_args)
        search_request = urllib2.Request(search_url, headers=authorization_header)
        search_response = urllib2.urlopen(search_request)
        search_data = json.loads(search_response.read())

        # Get user playlists
        tracks = search_data.get('tracks')
        items = tracks.get('items')
        if len(items) == 0:
            return {}

        preview_url = items[0].get('preview_url')
        return {'preview_url': preview_url}
