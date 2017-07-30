import subprocess

from models import initialize_sql
from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from sqlalchemy import engine_from_config

from .models import (
    Base,
)
from application.models.database import db


def main(global_config, **settings):
    my_session_factory = SignedCookieSessionFactory(
        'itsaseekreet')
    config = Configurator(settings=settings,
                          session_factory=my_session_factory)

    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)

    config.include('pyramid_jinja2')
    config.add_jinja2_search_path("static/templates")
    config.add_route('home', '/')
    config.add_route('about', '/about')
    config.add_route('contact', '/contact')

    config.add_route('playlists', '/playlists')
    config.add_route('suggestions', '/get-suggestions')

    config.add_route('results', '/result-playlist')
    config.add_route('select_playlist', '/select-playlist')
    config.add_route('select_spotify_playlist', '/select-spotify-playlist')
    config.add_route('refresh_spotify_token','/refresh-spotify-token')
    config.add_route('spotify_auth', '/spotify-auth')
    config.add_route('spotify_redirect', '/spotify-redirect')

    config.add_route('spotify_callback', '/spotify-callback')
    config.add_route('get_preview_url', '/get-preview-url')


    config.add_route('selected_playlist', '/show-selected-playlist')
    config.add_route('authorized', '/authorized')
    config.add_route('redirect', '/oauth2callback')
    config.add_static_view(name='static', path='application:static')
    config.add_static_view('images', 'static/images')
    config.add_static_view('js', 'static/js')

    config.scan('.views')
    subprocess.Popen(['/bin/bash', '-i', '-c', 'pgweb --url postgres://playgen:12345678@localhost:5432/playgen_db'])
    # subprocess.call('alembic revision --autogenerate -m ""')
    # subprocess.call('alembic upgrade head ""')

    return config.make_wsgi_app()
