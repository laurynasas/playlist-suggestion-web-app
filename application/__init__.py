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
    config.add_route('hello', '/howdy')
    config.add_route('authorized', '/authorized')
    config.add_route('redirect', '/oauth2callback')

    config.scan('.views')
    return config.make_wsgi_app()