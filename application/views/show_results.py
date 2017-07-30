from pyramid.view import (
    view_config
)

from application import db
from application.models.database import Song
from controllers.suggestions.get_suggestions import create_suggestion_list


class TutorialViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='results', renderer='results.jinja2')
    def results(self):

        user_playlist = self.request.POST.get('playlist')
        user_limit = int(self.request.POST.get('limit'))
        number_bands = int(self.request.POST.get('bands'))
        user_playlist = user_playlist.split(",")
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
