#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import hashlib


"""
access-method:
    http-ui r
    http-ui rw             (user: rw)
    git-over-http r
    git-over-http rw       (user: rw)

we don't support ftp-protocol since it does not support one-server-multiple-domain.
"""


def start(params):
    serverId = params["server-id"]
    domainName = params["domain-name"]
    dataDir = params["data-directory"]
    tmpDir = params["temp-directory"]
    webRootDir = params["webroot-directory"]

    # htdigest file
    htdigestFn = os.path.join(tmpDir, "auth-%s.htdigest" % (serverId))
    _Util.generateApacheHtdigestFile(htdigestFn, "webdav")

    # wsgi script
    wsgiFn = os.path.join(tmpDir, "wsgi-%s.py" % (serverId))
    with open(wsgiFn, "w") as f:
        buf = ''
        buf += '#!/usr/bin/python3\n'
        buf += '# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-\n'
        buf += '\n'
        buf += 'from wsgidav.fs_dav_provider import FilesystemProvider\n'
        buf += 'from wsgidav.wsgidav_app import WsgiDAVApp\n'
        buf += '\n'
        buf += 'config = {\n'
        buf += '    "provider_mapping": {"/": FilesystemProvider(%s)}\n' % (dataDir),
        buf += '    "verbose": 1,\n'
        buf += '    }\n'
        buf += 'application = WsgiDAVApp(config)\n'
        f.write(buf)

    # generate apache config segment
    buf = ''
    buf += 'ServerName %s\n' % (domainName)
    buf += 'DocumentRoot "%s"\n' % (webRootDir)
    buf += 'WSGIScriptAlias / %s\n' % (wsgiFn)
    buf += 'WSGIChunkedRequest On\n'
    buf += '\n'

    cfg = {
        "module-dependencies": [
            "mod_wsgi.so",
        ],
        "config-segment": buf,
    }
    privateData = None
    return (cfg, privateData)


def stop(private_data):
    pass


class _Util:

    @staticmethod
    def ensureDir(dirname):
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    @staticmethod
    def generateApacheHtdigestFile(filename, scope):
        # user "write", without password
        with open(filename, "w") as f:
            # username:scope:password-digest
            f.write('%s:%s:%s\n' % ("write", scope, hashlib.md5(':'.join(ui).encode("iso8859-1")).hexdigest()))
