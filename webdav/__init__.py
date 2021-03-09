#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import pathlib
import hashlib


"""
Access:
  PROTOCOL      URL                 USER        EFFECT
  http          http://...                      filemanager-ui,read-only
  http          http://...          ro          filemanager-ui,read-only
  http          http://...          rw          filemanager-ui,read-write
  http          http://.../pub                  httpdir
  webdav        http://.../dav                  webdav,read-only
  webdav        http://.../dav      ro          webdav,read-only
  webdav        http://.../dav      rw          webdav,read-write

Notes:
  1. We don't support ftp-protocol since it does not support one-server-multiple-domain.
  2. We have to use "pub" and "dav" subdirectory. Static files of filemanager-ui would conflict with the files being served if not doing so.
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
        buf = pathlib.Path(os.path.join(selfDir, "entry.py.in")).read_text()
        buf = buf.replace("%%WEBDAV_DIR%%", webdavDir)
        f.write(buf)

    # generate apache config segment
    buf = ''
    buf += 'ServerName %s\n' % (domainName)
    buf += 'DocumentRoot "%s"\n' % (webRootDir)
    buf += '<Directory "%s">\n' % (pubDir)
    buf += '    Options Indexes\n'
    buf += '    Require all granted\n'
    buf += '</Directory>\n'
    buf += 'WSGIScriptAlias /dav %s\n' % (wsgiFn)
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
