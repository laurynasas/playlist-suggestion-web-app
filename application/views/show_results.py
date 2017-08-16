import base64
import json
import time
import urllib
import urllib2

from pyramid.view import (
    view_config
)
from sqlalchemy import or_, and_

from application import db
from application.models.database import Song
from controllers.suggestions.get_suggestions import create_suggestion_list

# ---------------- SPOTIFY API -------------------------------------------------------

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

CLIENT_SECRETS_SPOTIFY = "d1e31b8f48b24e15aaa7c211b9970e8b"
CLIENT_ID_SPOTIFY = "b774e3bf851646c1b02928ea75802587"


# -------------------------------------------------------------------------------------


class ShowResults:
    def __init__(self, request):
        self.request = request

    def make_search_query(self, search_text):

        code_payload = {
            "q": search_text,
            "type": "track",
            "limit": "1"
        }

        authorization_header = {"Authorization": "Bearer {}".format(self.request.session.get('spotify_token'))}

        url_args = "&".join(["{}={}".format(key.encode("utf-8"), urllib.quote(val.encode("utf-8"))) for key, val in
                             code_payload.iteritems()])

        search_url = "{}/search?{}".format(SPOTIFY_API_URL, url_args)
        search_request = urllib2.Request(search_url, headers=authorization_header)
        search_response = urllib2.urlopen(search_request)

        return json.loads(search_response.read())

    def get_preview_urls(self, song_ids):
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
        print "len before exe", len(song_ids)

        for song_id in song_ids:
            song = db.query(Song).filter(Song.id == song_id).first()
            if song.preview_url:
                print "already have preview url and will be skipping"
                continue

            for query_type in [' - ','by', '-']:
                song_title = song.get_full_title().replace(" - ", query_type)
                search_results = self.make_search_query(song_title)

                tracks = search_results.get('tracks')
                items = tracks.get('items')
                if len(items) == 0:
                    continue

                if items[0].get('preview_url'):
                    song.preview_url = items[0].get('preview_url')
                    db.commit()
                    break

    @view_config(route_name='display_results', renderer='results.jinja2')
    def display_results(self):
        result_playlist = json.loads(self.request.POST.get('result_playlist'))
        return {'results': result_playlist}

    @view_config(route_name='compute_results', renderer='json')
    def compute_results(self):
        start = time.time()
        user_playlist = eval(self.request.GET.get('playlist'))
        user_limit = int(self.request.GET.get('limit'))
        number_bands = int(self.request.GET.get('bands'))

        result_list = create_suggestion_list(user_playlist, required_suggestions=user_limit,
                                             number_bands=number_bands)
        song_ids = []
        result_songs = {}
        if result_list:
            song_ids = [song.id for song, source in result_list]

        print "len result list beore sending", len(result_songs)
        p = time.time()
        self.get_preview_urls(song_ids)

        if result_list:
            for song, source in result_list:
                result_songs[song.id] = song.to_json()

        pp = time.time()
        print "Preview time:", pp - p
        end = time.time()
        print "Total time taken: ", (end - start)

        return {"result_playlist": result_songs}

    @view_config(route_name='suggestions', renderer='json')
    def get_suggestions(self):
        terms = self.request.GET.get('term')

        terms = terms.split("-")
        terms = [el.strip(" '\"-") for el in terms]
        all_songs = []
        if len(terms) == 1:
            all_songs = db.query(Song).filter(
                or_(Song.title.ilike("%" + terms[0] + "%"), Song.artist_title.ilike("%" + terms[0] + "%"))).limit(
                5).all()

        if not all_songs and len(terms) == 2:
            print "first"
            all_songs = db.query(Song).filter(
                and_(Song.title.ilike("%" + terms[0] + "%"), Song.artist_title.ilike("%" + terms[1] + "%"))).limit(
                5).all()

        if not all_songs and len(terms) == 2:
            print "sec"
            all_songs = db.query(Song).filter(
                and_(Song.title.ilike("%" + terms[1] + "%"), Song.artist_title.ilike("%" + terms[0] + "%"))).limit(
                5).all()

        titles = [song.title + " - " + song.artist_title for song in all_songs]
        print json.dumps(titles)

        return {'suggestions': json.dumps(titles)}
