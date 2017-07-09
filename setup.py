from setuptools import setup

requires = [
    'pyramid',
    'pyramid_jinja2',
]

setup(name='suggest_playlist',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = application:main
      """,
)