#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import hashlib

from werkzeug.utils import import_string


def checksum(path, limit):
    """Returns the file checksum limited length.

    :param path: path to the file
    :param limit: limit checksum string that value
    """
    h = hashlib.md5()
    try:
        with open(path, 'rb') as a_file:
            to_hash = a_file.read()
    except IOError:
        return

    h.update(to_hash)
    return h.hexdigest()[:limit]


key = lambda suffix: '%s_%s' % ('STATIC_UTILS', suffix)
"""Helper to create config keys."""


def to_class(path):
    """Returns object imported from path.

    :param path: path to the object
    """
    if not path:
        return

    module_name, class_name = path.rsplit('.', 1)
    module = import_string(module_name, silent=True)
    return getattr(module, class_name, None)


def abspath(path, root):
    """Returns an absolute version of the path starts from the root.

    :param path: path to transform
    :param root: where result starts from
    """
    if os.path.isabs(path):
        pass
    else:
        path = os.path.join(root, path)
    return path


def make_key(iden, *args, **kwargs):
    """Returns the cache-usable keys out of arbitrary arguments. All arguments
    and keywords hashed but leaves the `iden` human-readable.

    :param iden: human-readable key part
    :param args: additional arguments
    :param kwargs: additional keywords
    """
    h = hashlib.md5()

    def _conv(s):
        if isinstance(s, str):
            return s
        elif isinstance(s, unicode):
            return s.encode('utf-8')
        elif isinstance(s, (tuple, list)):
            return ','.join(map(_conv, s))
        elif isinstance(s, dict):
            return ','.join('%s:%s' % (_conv(k), _conv(v))
                            for k, v in sorted(s.iteritems()))
        else:
            return str(s)

    iden = _conv(iden)
    h.update(iden)
    h.update(_conv(args))
    h.update(_conv(kwargs))
    return '%s(%s)' % (iden, h.hexdigest())
