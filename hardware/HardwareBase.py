#!/usr/bin/python3.14
# -*- coding: utf-8 -*-


import sys
from utils import timestampEpoch


class HardwareBase:


    def __init__(self):
        """Initialize."""

        from utils import loggingGet, getPaths, jsonLoad, ApiClient
        self.logger = loggingGet(str(self.__class__.__name__).lower())

        self.paths = getPaths()

        self.ioSettings = jsonLoad(self.paths['io_settings']['path'], self.logger)

        self.apiClient = ApiClient(self.logger)

        self._setState('initializing')

        #

        if not self.state['value']['state'] == 'error': self._setState('ready')


        return

    def _setState(self, status, values={}, error=None):
        """Set component state."""

        self.state = {
            'timestamp': timestampEpoch(),
            'component': str(self.__class__.__name__).lower() if not hasattr(self, 'component') else self.component,
            'type': 'state',
            'value': dict(
                [
                    *[
                        ('state', status),
                        ('error', repr(error))
                    ],
                    *[
                        (k, values[k])
                        for k in values.keys()
                    ]
                ]
            ),
            'pending': False
        }

        if status == 'error':

            if hasattr(self, 'logger'):

                self.logger.error(' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), repr(error)]))

        # TODO: API


        return
