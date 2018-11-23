# -*- coding: utf-8 -*-
# flake8: noqa
from setuptools import find_packages, setup

entry_points = """
[console_scripts]
run_web=manage:runserver
init_db=manage:create_db
"""

setup(
    name='zheye',
    version='0.0.1',
    license='PRIVATE',
    author='',
    author_email='',
    url='https://github.com/mathbugua/zheye',
    description=u'zheye',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    install_requires=[
        'Flask',
        'Flask-Bootstrap',
        'Flask-Login',
        'Flask-Mail',
        'Flask-Migrate',
        'Flask-Moment',
        'Flask-SQLAlchemy',
        'Flask-Script',
        'Flask-WTF',
        'Jinja2',
        'Mako',
        'Markdown',
        'Flask-PageDown',
        'MarkupSafe',
        'SQLAlchemy',
        'WTForms',
        'Werkzeug',
        'alembic',
        'blinker',
        'itsdangerous',
        'six',
        'bleach',
        'click',
        'html5lib',
        'python-editor',
        'Flask-HTTPAuth',
        'tornado',
    ],
    entry_points=entry_points,
)
