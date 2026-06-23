#!/usr/bin/python3.14
# -*- coding: utf-8 -*-


from . import paths, apiSettings, server, display, displayCurrentFilePath, orientation, database
from flask import jsonify, request, send_file
from werkzeug.utils import secure_filename


@server.route('/api/<path:apiVersion>/ping', methods=['GET'])
def ping(apiVersion):
    """Responds when server is running."""


    return jsonify({'status': 'ok', 'api_version': apiVersion}), 200


@server.route('/api/<path:apiVersion>/metadata/<path:metaPath>/<path:subPath>', methods=['GET', 'PUT', 'POST', 'DELETE'])
def media(apiVersion, metaPath, subPath):
    """Media routing handler."""

    if apiVersion == 'v1':

        if request.method == 'GET':

            if len(subPath) > 0:

                if metaPath == 'metadata' and subPath == 'all':

                    return jsonify({'status': 'ok', 'api_version': apiVersion, 'data': database.metadataGet()}), 200

                elif metaPath == 'media' and '.' in subPath and not '/' in subPath:

                    return downloadMediaFile__v1(subPath)

        elif request.method == 'PUT':

            if len(subPath) > 0:

                if metaPath == 'playlist' and subPath == 'new':

                    pass # TODO:

                elif metaPath == 'media' and subPath == 'new':

                    return uploadMediaFile__v1(requestData)

        elif request.method == 'POST':

            if len(subPath) > 0:

                if metaPath == 'playlist' and len(subPath) > 0:

                    pass # TODO:

                elif metaPath == 'media' and  '.' in subPath and not '/' in subPath:

                    requestData = request.json

                    if isinstance(requestData, dict):

                        if not 'file' in requestData.keys(): requestData['file'] = subPath.split('?')[0]

                        database.metadataMediaUpdate(requestData)

                        return jsonify({'status': 'ok', 'api_version': apiVersion}), 200

        elif request.method == 'DELETE':

            if len(subPath) > 0:

                if metaPath == 'playlist' and len(subPath) > 0:

                    pass # TODO:

                elif metaPath == 'media' and '.' in subPath and not '/' in subPath:

                    requestData = request.json

                    if isinstance(requestData, dict):

                        if not 'file' in requestData.keys(): requestData['file'] = subPath.split('?')[0]

                        database.metadataMediaDelete(requestData)

                        return jsonify({'status': 'ok', 'api_version': apiVersion}), 200


    return jsonify({'error': 'Bad Request', 'api_version': apiVersion}), 400

# Download media file
def downloadMediaFile__v1(fileName):
    """Download media file if exists."""

    #queryParams = fileName.split('?', 2)[-1]
    fileName = fileName.split('?')[0]

    existingMedia = database.metadataMediaFileExists(fileName)

    if isinstance(existingMedia, dict):

        return send_file(existingMedia['path']), 200


    return jsonify({'error': 'Not Found', 'api_version': 'v1'}), 404
# Upload media file
def uploadMediaFile__v1():
    """Upload file."""

    requestFile = request.files['file']

    if requestFile is None:

        return jsonify({'status': 'error', 'error': 'Bad Request', 'api_version': 'v1', 'detail': 'no file'}), 400

    else:

        requestSecureFileName = secure_filename(requestFile.filename)

        if len(requestSecureFileName) > 0 and '.' in requestSecureFileName:

            requestFileExtension = requestSecureFileName.split('.')[-1]

            if len(requestFileExtension) > 0 and requestFileExtension in apiSettings['upload_extensions']:

                import os

                tempPath = os.path.join(
                    paths['temp']['path'],
                    requestSecureFileName
                )
                localPath = os.path.join(
                    paths['media']['path'],
                    requestSecureFileName
                )

                existingMedia = database.metadataMediaFileExists(requestSecureFileName)

                if isinstance(existingMedia, dict) or (isinstance(existingMedia, bool) and existingMedia == False):

                    requestFile.save(tempPath)

                    from utils.Imager import Imager

                    imager = Imager()
                    imager.setDisplayOrientation(orientation['orientation']['orientation'] if 'orientation' in orientation.keys() else 'landscape')

                    requestFileInfo = imager.getImageInfo(tempPath)

                    if len(requestFileInfo.keys()) > 0:

                        os.rename(tempPath, localPath)

                        requestFileInfo['type'] = 'original'
                        requestFileInfo['file'] = requestSecureFileName
                        requestFileInfo['uri'] = '/media/%(request_secure_file_name)s' % {
                            'request_secure_file_name': requestSecureFileName
                        }
                        requestFileInfo['path'] = localPath
                        requestFileInfo['thumbnails'] = imager.generateThumbnails(localPath)

                        if len(requestFileInfo['thumbnails']) > 0:

                            for t in range(len(requestFileInfo['thumbnails'])):

                                requestFileInfo['thumbnails'][t]['uri'] = '/media/%(request_secure_file_name)s' % {
                                    'file': requestFileInfo['thumbnails'][t]['file']
                                }

                                # Update and save metadata
                                database.metadataMediaAdd(requestFileInfo)

                                return jsonify({'status': 'ok', 'api_version': 'v1'}), 200

                        else:

                            return jsonify({'status': 'error', 'error': 'Internal Server Error', 'api_version': 'v1', 'detail': 'unable to generate thumbnails'}), 500

                    else:

                        return jsonify({'status': 'error', 'error': 'Bad Request', 'api_version': 'v1', 'detail': 'unsupported image format'}), 400

            else:

                return jsonify({'status': 'error', 'error': 'Bad Request', 'api_version': 'v1', 'detail': 'unsupported file extension'}), 400

        else:

            return jsonify({'status': 'error', 'error': 'Bad Request', 'api_version': 'v1', 'detail': 'filename insecure'}), 400


    return jsonify({'status': 'error', 'error': 'Internal Server Error', 'api_version': 'v1'}), 500




@server.route('/api/<path:apiVersion>/hardware/<path:hardwarePath>', methods=['GET', 'PUT', 'POST'])
def hardware(apiVersion, hardwarePath):
    """Hardware routing handler."""

    if apiVersion == 'v1':

        if len(hardwarePath) > 0:

            if hardwarePath == 'state':

                if request.method == 'GET':

                    return jsonify({'status': 'ok', 'api_version': apiVersion, 'data': database.stateGet(stateType='state')}), 200

                elif request.method == 'POST':

                    requestData = request.json

                    if isinstance(requestData, dict):

                        database.stateUpdate(requestData)

                        return jsonify({'status': 'ok', 'api_version': apiVersion}), 200

            elif hardwarePath == 'event':

                if request.method == 'GET':

                    return jsonify({'status': 'ok', 'api_version': apiVersion, 'data': database.stateGet(stateType='event')}), 200

                elif request.method == 'PUT':

                    requestData = request.json

                    if isinstance(requestData, dict):

                        database.stateAdd(requestData)

                        return jsonify({'status': 'ok', 'api_version': apiVersion}), 200

                elif request.method == 'POST':

                    requestData = request.json

                    if isinstance(requestData, dict):

                        database.stateUpdate(requestData)

                        return jsonify({'status': 'ok', 'api_version': apiVersion}), 200


    return jsonify({'error': 'Bad Request', 'api_version': apiVersion}), 400


# Hardware
def displayMediaFile__v1(fileName):
    """Display media."""

    #queryParams = fileName.split('?', 2)[-1]
    fileName = fileName.split('?')[0]

    existingMedia = database.metadataMediaFileExists(fileName)

    if isinstance(existingMedia, dict):

        if not display is None:

            from utils.Imager import Imager

            imager = Imager()
            imager.setDisplayOrientation(orientation['orientation']['orientation'] if 'orientation' in orientation.keys() else 'landscape')

            quantizedBuffer = imager.getQuantizedBuffer(existingMedia['path'])

            if len(quantizedBuffer) > 0:

                if display.state == 'ready':

                    display.displayBufferedBytes(quantizedBuffer)
                    displayCurrentFilePath = existingMedia['path']

                else:

                    return jsonify({'status': 'error', 'error': 'Internal Server Error', 'api_version': 'v1', 'detail': 'display not ready'}), 500

            else:

                return jsonify({'status': 'error', 'error': 'Internal Server Error', 'api_version': 'v1', 'detail': 'unable to quantize image'}), 500

        else:

            return jsonify({'status': 'error', 'error': 'Internal Server Error', 'api_version': 'v1', 'detail': 'display not initialized'}), 500

    else:

            return jsonify({'status': 'error', 'error': 'Not Found', 'api_version': 'v1'}), 404


    return jsonify({'status': 'error', 'error': 'Internal Server Error', 'api_version': 'v1'}), 500
def orientationUpdate__v1(orientationValues):
    """Update orientation values."""

    if 'orientation' in orientation.keys() and 'orientation' in orientationValues.keys():

        if not orientationValues['orientation']['orientation'] == orientation['orientation']['orientation']:

            orientation = orientationValues

            if len(displayCurrentFilePath) > 0:

                import os

                return displayMediaFile__v1(
                    displayCurrentFilePath.split(os.sep)[-1]
                )

        orientation = orientationValues

        return jsonify({'status': 'ok', 'api_version': 'v1'}), 200


    return jsonify({'error': 'Bad Request', 'api_version': 'v1'}), 400


def initHardware():
    """Initialize hardware."""

    from hardware.Display import Display

    display = Display()


    return


# Static files
def serveStatic():
    """Serve static files."""

    import os

    if request.method == 'GET':

        for pathKey in paths.keys():

            if paths[pathKey]['publish'] == True:

                if not request.path.strip('/').split('?')[0].startswith('.'):

                    # Insecure and inefficient
                    localPath = os.path.join(
                        paths[pathKey]['path'],
                        request.path.strip('/').split('?')[0]
                    )

                    if os.path.exists(localPath):

                        return send_file(localPath), 200


    return jsonify({'error': 'Not Found'}), 404
def initStatic():
    """Initialize static routes."""

    for pathKey in paths.keys():

        if paths[pathKey]['publish'] == True:

            _initStaticPath(
                paths[pathKey]['path'],
                paths[pathKey]['path']
            )


    return
def _initStaticPath(staticPath, basePath):
    """Initialize static routes within path."""

    import os
    from glob import glob

    for pathChild in glob(os.path.join(staticPath, '*')):

        if os.path.isdir(pathChild):

            _initStaticPath(
                pathChild,
                basePath
            )

        else:

            staticFile = pathChild.rsplit(os.sep, 1)[-1].strip('/').strip('\\')

            if not staticFile.startswith('.'):

                routePath = staticPath[len(basePath):].strip('/').strip('\\').replace('\\', '/') if len(staticPath) > len(basePath) else ''

                server.add_url_rule(
                    '/%(route_path)s%(sep)s%(file_path)s' % {
                        'route_path': routePath,
                        'sep': '/' if len(routePath) > 0 else '',
                        'file_path': staticFile
                    },
                    'serveStatic',
                    serveStatic,
                    methods=['GET']
                )


    return


# Run
def serverRun():
    """Run server."""

    from os import environ

    HOST = environ.get(
        'PAPER_SERVER_HOST',
        'localhost'
    )
    PORT = int(
        environ.get(
            'PAPER_SERVER_PORT',
            '5000'
        )
    )


    server.run(HOST, PORT)
