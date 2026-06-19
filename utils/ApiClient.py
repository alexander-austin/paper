#!/usr/bin/python3.14
# -*- coding: utf-8 -*-


import json, requests, sys


class ApiClient:


    def __init__(self, logger=None):
        """Initialize."""

        self.logger = logger

        from utils import getPaths, jsonLoad

        self.paths = getPaths()
        self.apiSettings = jsonLoad(self.paths['api_settings']['path'])


        return


    def sendRequest(self, method='GET', endpoint='/api/<api_version>/ping', requestData=None, timeout=3.0):
        """Send request to API."""

        responseStatus = None
        responseJson = None

        try:

            response = None

            endpoint = endpoint.replace('<api_version>', self.apiSettings['api_version'])

            requestUrl = '%(protocol)s://%(host)s:%(port)d%(endpoint)s' % {
                'protocol': self.apiSettings['protocol'],
                'host': self.apiSettings['host'],
                'port': self.apiSettings['port'],
                'endpoint': endpoint
            }

            requestHeaders = {
                'Accept': 'application/json'
            } if requestData is None else {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }

            if not requestData is None: requestData = json.dumps(requestData)

            if method == 'GET':

                response = requests.get(
                    url=requestUrl,
                    headers=requestHeaders,
                    data=requestData,
                    timeout=timeout
                )

            elif method == 'PUT':

                response = requests.put(
                    url=requestUrl,
                    headers=requestHeaders,
                    data=requestData,
                    timeout=timeout
                )

            elif method == 'POST':

                response = requests.post(
                    url=requestUrl,
                    headers=requestHeaders,
                    data=requestData,
                    timeout=timeout
                )

            elif method == 'DELETE':

                response = requests.delete(
                    url=requestUrl,
                    headers=requestHeaders,
                    data=requestData,
                    timeout=timeout
                )

            if not response is None:

                responseStatus = response.status_code

                if response.status_code == 200:

                    try:

                        responseJsonTemp = response.json()

                        responseJson = responseJsonTemp

                    except: pass

        except Exception as e:

            if not self.logger is None:

                if responseStatus is None: responseStatus = ' '.join(['client error', repr(e)])

                self.logger.error(' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), repr(e)]))


        return responseStatus, responseJson
