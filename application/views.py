import httplib2
from apiclient.discovery import build
from controllers.get_youtube_playlist import list_playlists_mine, create_playlists, playlist_items_list_by_playlist_id, \
    get_playlist_songs
from controllers.suggestions.get_suggestions import create_suggestion_list
from controllers.suggestions.network import load_network_with_songs
from oauth2client import client
from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    view_config
)

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = '/home/laurynas/workspace/suggest_playlist/application/client_secrets.json'

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.force-ssl"
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = "WARNING: Please configure OAuth 2.0"
NUMBER_SOURCES = 1000
NETWORK_DIR = "/home/laurynas/workspace/suggest_playlist/application/resources/network.txt"
SONGS_DIR = "/home/laurynas/workspace/suggest_playlist/application/resources/songs_already_visited.txt"


class TutorialViews:
    def __init__(self, request):
        self.request = request
        self.network = load_network_with_songs(NETWORK_DIR, SONGS_DIR, NUMBER_SOURCES)

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

            playlists_instances = create_playlists(playlists_info)
            #
            # playlist = playlist_items_list_by_playlist_id(service,
            #                                               part='snippet,contentDetails',
            #                                               maxResults=25,
            #                                               playlistId='PL4CnV3w6P34VBu2llSwQ7bDCuJ14HfL2h')

            return {'playlists': playlists_instances}

    @view_config(route_name='home', renderer='playlist.jinja2')
    @view_config(route_name='home', request_param='insert=1', renderer='playlist-insert.jinja2')
    def show_songs(self):
        titles = self.network.prepare_songs_search_box()
        playlist_id = self.request.POST.get('playlist_id')
        insert = 0

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

                playlist_songs = get_playlist_songs(playlist_info)

                return {'playlist': playlist_songs, 'suggestions': titles, 'playlist_id': playlist_id}
        else:
            return {'suggestions': titles}

    @view_config(route_name='results', renderer='results.jinja2')
    def results(self):
        print "results"

        user_playlist = self.request.POST.get('playlist')
        user_limit = int(self.request.POST.get('limit'))
        number_bands = int(self.request.POST.get('bands'))
        user_playlist = user_playlist.split(",")
        result_list = create_suggestion_list(user_playlist, self.network, required_suggestions=user_limit,
                                             number_bands=number_bands)
        if result_list:
            result_list = [song for song, source in result_list]
        return {"result_playlist": result_list}

    @view_config(route_name='about', renderer='about.jinja2')
    def about(self):
        return {}

    @view_config(route_name='contact', renderer='contact.jinja2')
    def contact(self):
        return {}

    @view_config(route_name='redirect')
    def oauth2callback(self):
        print "AGAAIN"
        flow = client.flow_from_clientsecrets(
            CLIENT_SECRETS_FILE,
            scope=YOUTUBE_READ_WRITE_SSL_SCOPE,
            redirect_uri=self.request.route_url('redirect'))
        flow.params['include_granted_scopes'] = 'true'
        if 'code' not in self.request.GET:
            auth_uri = flow.step1_get_authorize_url()
            print "not found  code in url"
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

            return HTTPFound(location=self.request.route_url('select_playlist'))

            # @view_config(route_name='hello')
            # def hello(self):
            #     return {'name': 'Hello View'}
