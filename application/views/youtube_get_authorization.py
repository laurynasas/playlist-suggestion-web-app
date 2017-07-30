from oauth2client import client
from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    view_config
)



# ---------------- YOUTUBE API -------------------------------------------------------
# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.

# The CLIENT_SECRETS_FILE_YOUTUBE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret
CLIENT_SECRETS_FILE_YOUTUBE = "/home/sensitive/client_secrets_youtube.json"
YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"

# -------------------------------------------------------------------------------------


class YoutubeAuthorize:
    def __init__(self, request):
        self.request = request

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
