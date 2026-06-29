#!/usr/bin/python3.14
# -*- coding: utf-8 -*-


import sys, threading
from utils import timestampEpoch


class HardwareBase:


    def __init__(self, *args, **kwargs):
        """Initialize."""

        self.args = list(args)
        for key, value in kwargs.items(): setattr(self, key, value)

        self.source = str(self.__class__.__name__).lower()

        from utils import loggingGet, getPaths, jsonLoad, ApiClient
        self.logger = loggingGet(self.source)

        self.paths = getPaths()

        self.ioSettings = jsonLoad(self.paths['io_settings']['path'], self.logger)

        self.apiClient = ApiClient(self.logger)

        self._setState('initializing')


        return

    def _setState(self, status, values={}, error=None, sendToApi=True):
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

        if sendToApi == True:

            apiRequest = threading.Thread(
                target=self.apiClient.sendRequest,
                kwargs={
                    'method': self.ioSettings['state_event']['endpoints']['state']['update']['method'],
                    'endpoint': self.ioSettings['state_event']['endpoints']['state']['update']['endpoint'],
                    'timeout': 3.0,
                    'requestData': self.state
                },
                daemon=False
            )
            apiRequest.start()


        return
    def _getEvents(self):
        """Get events."""

        responseStatus, responseJson = self.apiClient.sendRequest(
            method=self.ioSettings['state_event']['endpoints']['event']['get']['method'],
            endpoint=self.ioSettings['state_event']['endpoints']['event']['get']['endpoint'],
            timeout=3.0
        )

        if responseStatus == 200:

            if isinstance(responseJson, dict):

                if 'data' in responseJson:

                    return responseJson['data']


        return []
    def _addEvent(self, values={}):
        """Send component event."""

        newEvent = {
            'timestamp': timestampEpoch(),
            'component': str(self.__class__.__name__).lower() if not hasattr(self, 'component') else self.component,
            'type': 'event',
            'value': dict(
                [
                    *[
                        ('source', self.source)
                    ],
                    *[
                        (k, values[k])
                        for k in values.keys()
                    ]
                ]
            ),
            'pending': True
        }

        if self.ioSettings[str(self.__class__.__name__).lower()]['pin_owner'] == True:

            for pinKey in self.ioSettings['pins']:

                if self.ioSettings['pins'][pinKey]['owner'] == str(self.__class__.__name__).lower() and self.ioSettings['pins'][pinKey]['active'] == True:

                    if 'intent' in self.ioSettings['pins'][pinKey].keys():

                        newEvent['value']['intent'] = self.ioSettings['pins'][pinKey]['intent']
                        break

        else:

            if 'intent' in self.ioSettings[str(self.__class__.__name__).lower()].keys():

                newEvent['value']['intent'] = self.ioSettings[str(self.__class__.__name__).lower()]['intent']

        apiRequest = threading.Thread(
            target=self.apiClient.sendRequest,
            kwargs={
                'method': self.ioSettings['state_event']['endpoints']['event']['add']['method'],
                'endpoint': self.ioSettings['state_event']['endpoints']['event']['add']['endpoint'],
                'timeout': 3.0,
                'requestData': newEvent
            },
            daemon=False
        )
        apiRequest.start()


        return
    def _updateEvent(self, eventToUpdate):
        """Update event."""

        self.apiClient.sendRequest(
            method=self.ioSettings['state_event']['endpoints']['event']['update']['method'],
            endpoint=self.ioSettings['state_event']['endpoints']['event']['update']['endpoint'],
            timeout=3.0,
            requestData=eventToUpdate
        )


        return
