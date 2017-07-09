import json

import httplib2
from apiclient import discovery
from apiclient.discovery import build
from oauth2client import client
from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    view_config
)

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = "WARNING: Please configure OAuth 2.0"


class TutorialViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='home', renderer='json')
    def index(self):
        print "Im home  "
        if 'credentials' not in self.request.session:
            return HTTPFound(location=self.request.route_url('redirect'))
        credentials = client.OAuth2Credentials.from_json(self.request.session['credentials'])
        if credentials.access_token_expired:
            return HTTPFound(location=self.request.route_url('redirect'))
        else:
            http_auth = credentials.authorize(httplib2.Http())
            youtube = discovery.build('youtube', 'v3', http_auth)
            channel = youtube.channels().list(mine=True, part='snippet').execute()

            service = build(API_SERVICE_NAME, API_VERSION,
                            http=credentials.authorize(httplib2.Http()))

            playlists = list_playlists_mine(service,
                                           part='snippet,contentDetails',
                                           mine=True)

            create_playlists(playlists, service)

            playlist = playlist_items_list_by_playlist_id(service,
                                                          part='snippet,contentDetails',
                                                          maxResults=25,
                                                          playlistId='PL4CnV3w6P34VBu2llSwQ7bDCuJ14HfL2h')

            return json.dumps(playlist)

    @view_config(route_name='authorized', renderer='home.jinja2')
    def authorized(self):
        print "Authorized"
        return {}

    @view_config(route_name='redirect')
    def oauth2callback(self):
        print "AGAAIN"
        flow = client.flow_from_clientsecrets(
            '/home/laurynas/workspace/suggest_playlist/application/client_secrets.json',
            scope='https://www.googleapis.com/auth/youtube.force-ssl',
            redirect_uri=self.request.route_url('redirect'))
        flow.params['include_granted_scopes'] = 'true'
        print self.request.GET
        if 'code' not in self.request.GET:
            auth_uri = flow.step1_get_authorize_url()
            print "not found  code in url"
            print self.request.urlvars
            print self.request.urlargs
            return HTTPFound(location=auth_uri)
        else:
            print "Foound code in url"
            auth_code = self.request.GET.get('code')
            credentials = flow.step2_exchange(auth_code)
            self.request.session['credentials'] = credentials.to_json()

            service = build(API_SERVICE_NAME, API_VERSION,
                            http=credentials.authorize(httplib2.Http()))

            print list_playlists_mine(service,
                                     part='snippet,contentDetails',
                                     mine=True)

            return HTTPFound(location=self.request.route_url('authorized'))

            # @view_config(route_name='hello')
            # def hello(self):
            #     return {'name': 'Hello View'}


def print_results(results):
    print(results)


# Remove keyword arguments that are not set
def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.iteritems():
            if value:
                good_kwargs[key] = value
    return good_kwargs


### END BOILERPLATE CODE

# Sample python code for channels.list

def list_playlists_mine(service, **kwargs):
    kwargs = remove_empty_kwargs(**kwargs)  # See full sample for function
    results = service.playlists().list(
        **kwargs
    ).execute()
    return results


def playlist_items_list_by_playlist_id(service, **kwargs):
    kwargs = remove_empty_kwargs(**kwargs)  # See full sample for function
    results = service.playlistItems().list(
        **kwargs
    ).execute()
    return results


def get_playlist_songs(service, playlist_id):
    playlist = playlist_items_list_by_playlist_id(service,
                                                  part='snippet,contentDetails',
                                                  maxResults=50,
                                                  playlistId=playlist_id)

    for song in playlist[u'items']:
        print song[u'snippet'][u'title']

def create_playlists(playlists, service):
    titles_by_ids = {}
    for playlist in playlists[u'items']:
        titles_by_ids[playlist[u'id']] = (playlist[u'snippet'][u'title'])
        print "--------", playlist[u'snippet'][u'title'], "---------------"
        get_playlist_songs(service, playlist[u'id'])
