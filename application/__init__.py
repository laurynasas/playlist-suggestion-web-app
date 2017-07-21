from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory


def main(global_config, **settings):

    my_session_factory = SignedCookieSessionFactory(
        'itsaseekreet')
    config = Configurator(settings=settings,
                          session_factory=my_session_factory)


    config.include('pyramid_jinja2')
    config.add_jinja2_search_path("templates")
    config.add_route('home', '/')
    config.add_route('about', '/about')
    config.add_route('contact', '/contact')

    config.add_route('playlists', '/playlists')
    config.add_route('results', '/result-playlist')
    config.add_route('select_playlist', '/select-playlist')


    config.add_route('selected_playlist', '/show-selected-playlist')
    config.add_route('authorized', '/authorized')
    config.add_route('redirect', '/oauth2callback')
    config.add_static_view(name='static', path='application:static')
    config.add_static_view('images', 'static/images')
    config.scan('.views')
    return config.make_wsgi_app()