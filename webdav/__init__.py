#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import hashlib


"""
    URL                 USER        EFFECT
    http://...                      http-ui,read-only
    http://...          ro          http-ui,read-only
    http://...          rw          http-ui,read-write
    http://.../pub                  httpdir
    http://.../pub      ro          httpdir
    http://.../pub      rw          httpdir
    http://.../dav                  http-webdav,read-only
    http://.../dav      ro          http-webdav,read-only
    http://.../dav      rw          http-webdav,read-write

we don't support ftp-protocol since it does not support one-server-multiple-domain.
"""


def start(params):
    serverId = params["server-id"]
    domainName = params["domain-name"]
    dataDir = params["data-directory"]
    tmpDir = params["temp-directory"]
    webRootDir = params["webroot-directory"]

    # pub directory in root directory
    pubDir = os.path.join(webRootDir, "pub")
    os.symlink(dataDir, pubDir)

    # webdav directory in root directory
    webdavDir = os.path.join(webRootDir, "dav")
    os.symlink(dataDir, webdavDir)

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
    buf += 'WSGIPassAuth On\n'
    # buf += 'WSGIChunkedRequest On\n'
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
