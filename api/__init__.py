#!/usr/bin/python3.14
# -*- coding: utf-8 -*-


__all__ = ['ping', 'serveStatic', 'initStatic', 'media', 'hardware', 'initHardware']


import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from utils import getPaths, jsonLoad


paths = getPaths()
apiSettings = jsonLoad(paths['api_settings']['path'])
display = None

server = Flask(apiSettings['name'])
server.wsgi_app = ProxyFix(
    server.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
    x_prefix=1
)


from .data import ping, serveStatic, initStatic, media, hardware, initHardware

initStatic()
initHardware()
