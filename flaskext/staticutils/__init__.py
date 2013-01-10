#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from functools import wraps
from flask import current_app, redirect
from werkzeug.contrib.cache import SimpleCache

from .utils import key, to_class, checksum, abspath, make_key


cache = SimpleCache()


def memoize(iden=None, timeout=60*60*24):
    """Decorator which cache result of function on simple in-memory cache.

    :param iden: the human-readable part of the cache key
    :param timeout: how long store result in cache
    :param fn: function that will be cached
    """
    def wrapper(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            key = make_key(iden or fn.__name__, *args, **kwargs)
            rv = cache.get(key)
            if rv is not None:
                return rv
            rv = fn(*args, **kwargs)
            cache.set(key, rv, timeout)
            return rv
        return wrapped
    return wrapper


class StaticUtils(object):
    """Inject assets revisions into Flask.

    :param app: Flask application instance
    """

    def __init__(self, app=None):
        self.app = app

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize extension settings from the application settings.

        :param app: Flask application instance
        """
        config = app.config
        config.setdefault(key('REV_FORMAT'), '%(path)s-%(rev)s%(ext)s')
        config.setdefault(key('FILTER_NAME'), 'rev')
        config.setdefault(key('REV_LENGTH'), 12)
        config.setdefault(key('REV_GENERATOR'), 'flask.ext.staticutils.FileChecksumRev')

        cls = to_class(config[key('REV_GENERATOR')])
        self._rev = cls(config[key('REV_FORMAT')])

        app.jinja_env.filters.setdefault(config[key('FILTER_NAME')], self)

        if app.testing:
            rule = '/<path:asset>-<string(maxlength=%s):rev><string:ext>'
            @app.route(rule % config[key('REV_LENGTH')])
            def static_revision(asset, rev, ext):
                return redirect('%s%s' % (asset, ext))

    @memoize('staticutils')
    def __call__(self, asset):
        """Returns the asset path with revision info.

        That value calculated only on-demand (on first call) and than cached for
        future usage, to avoid having to do a disk read as well as to avoid that
        computation for each request.

        :param asset: path to asset
        """
        return self._rev(asset)


class IRev(object):
    """Implements default interfaces to generate asset path with revision info.

    :param formatstr: format string used to produce asset path
    """

    def __init__(self, formatstr):
        self.formatstr = formatstr

    def __call__(self, asset):
        """Rewrite asset value with revision info. Must be implemented on
        subclasses.

        :param asset: path to asset
        """
        raise NotImplementedError


class FileChecksumRev(IRev):
    """Use file checksum as revision string."""

    def __call__(self, asset):
        path = abspath(asset, current_app.root_path)
        rev = checksum(path, current_app.config[key('REV_LENGTH')])
        if rev is None:
            return asset

        path, ext = os.path.splitext(asset)
        return self.formatstr % dict(path=path, ext=ext, rev=rev)
