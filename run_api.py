#!/usr/bin/python3.14
# -*- coding: utf-8 -*-


if __name__ == '__main__':

    import api
    from os import environ

    HOST = environ.get(
        '%(name)s_SERVER_HOST' % {
            'name': api.apiSettings['name'].upper()
        },
        'localhost'
    )
    PORT = int(
        environ.get(
            '%(name)s_SERVER_PORT' % {
                'name': api.apiSettings['name'].upper()
            },
            '5000'
        )
    )


    api.server.run(HOST, PORT)
