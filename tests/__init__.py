#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from attest import Tests, assert_hook, AssertImportHook

# disable assert hook before load flask app, while pull-request will be
# accepted https://github.com/dag/attest/pull/136
AssertImportHook.disable()

from flaskext.staticutils import StaticUtils
from flaskext.staticutils.utils import checksum, key, abspath, make_key

from tests.test_app import create_app


utils = Tests()


@utils.test
def existing_file_checksum():
    path = os.path.join(os.getcwd(), 'requirements.dev.txt')
    must_be = '0cef80c690b7529d44b332fc'
    h = checksum(path, 24)
    assert h == must_be
    assert len(h) <= 24


@utils.test
def nonexisting_file_checksum():
    assert checksum('nosuchfile', 10) is None


@utils.test
def _abspath():
    root = '/'
    path = abspath('foo', root)
    assert os.path.isabs(path)
    assert path.startswith(root)


@utils.test
def _make_key():
    key1 = make_key('foo')
    key2 = make_key('foo', a=1, b=2)
    assert 'foo' in key1
    assert 'foo' in key2
    assert key1 != key2


staticutils = Tests()


def setup(app):
    rev = StaticUtils(app)
    return app, rev


@staticutils.context
def app_context():
    app = create_app({})

    with app.test_request_context():
        yield app


@staticutils.test
def instance(app):
    _, rev = setup(app)
    assert app is not None
    assert app.jinja_env.filters[app.config[key('FILTER_NAME')]] is rev


@staticutils.test
def existing_file_default_formatstr(app):
    _, rev = setup(app)
    assert rev('static/js/app.js') == 'static/js/app-1b42a11f5f64.js'


@staticutils.test
def existing_file_custom_formatstr(app):
    app.config[key('REV_FORMAT')] = 'rev-%(rev)s/%(path)s%(ext)s'
    _, rev = setup(app)
    assert rev('static/js/app.js') == 'rev-1b42a11f5f64/static/js/app.js'


@staticutils.test
def nonexisting_file(app):
    _, rev = setup(app)
    assert rev('nosuchfile') == 'nosuchfile'


@staticutils.test
def template_render(app):
    setup(app)
    with app.test_client() as c:
        rv = c.get('/')
        assert 'static/js/app-1b42a11f5f64.js' in rv.data


@staticutils.test
def rewrite_rule(app):
    setup(app)
    with app.test_client() as c:
        assert app.testing
        rv = c.get('static/js/app-d41d8cd98f00.js')
        assert rv.status_code == 302
        assert rv.headers['Location'] == 'http://localhost/static/js/app.js'

        rv = c.get('static/js/app-d41d8cd98f00.js', follow_redirects=True)
        assert rv.data == 'well\n'


suite = Tests(tests=(utils, staticutils))


if __name__ == '__main__':
    suite.main()
