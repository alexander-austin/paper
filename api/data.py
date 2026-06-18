#!/usr/bin/python3.14
# -*- coding: utf-8 -*-


from . import paths, apiSettings, server
from flask import jsonify, make_response, request, send_file
from werkzeug.utils import secure_filename


@server.route('/api/<path:apiVersion>/ping', methods=['GET'])
def ping(apiVersion):
    """Responds when server is running."""


    return jsonify({'status': 'ok', 'api_version': apiVersion}), 200


@server.route('/api/<path:apiVersion>/media/<path:mediaPath>', methods=['GET', 'PUT', 'POST', 'DELETE'])
def media(apiVersion, mediaPath):
    """Media routing handler."""

    if apiVersion == 'v1':

        if request.method == 'GET':

            if len(mediaPath) > 0:

                if mediaPath == 'all':

                    return jsonify({'status': 'ok', 'api_version': apiVersion, 'data': metadataFormatted()}), 200

                elif '.' in mediaPath:

                    pass

        elif request.method == 'PUT':

            if mediaPath == 'new':

                return uploadMediaFile__v1()

        elif request.method == 'POST':

            pass

        elif request.method == 'DELETE':

            pass


    return jsonify({'error': 'Bad Request', 'api_version': apiVersion}), 400


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

                if not metadataFileNameExists(requestSecureFileName) and not os.path.exists(tempPath) and not os.path.exists(localPath):

                    requestFile.save(tempPath)

                    from utils.Imager import Imager

                    imager = Imager()

                    requestFileInfo = imager.getImageInfo(tempPath)

                    if len(requestFileInfo.keys()) > 0:

                        os.rename(tempPath, localPath)

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
                                metadataAppendMedia(requestFileInfo)

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


# Metadata
def metadataFileNameExists(fileName, checkThumbnails=True):
    """Check whether file name exists in metadata."""

    from utils import jsonLoad

    metadata = jsonLoad(paths['metadata']['path'])

    for media in metadata['media']:

        if media['file'] == fileName:

            return True
        
        if checkThumbnails == True:

            for mediaThumbnail in media['thumbnails']:

                if mediaThumbnail['file'] == fileName:

                    return True


    return False
def metadataAppendMedia(media):
    """Append media to metadata."""

    from utils import jsonLoad, jsonSave

    metadata = jsonLoad(paths['metadata']['path'])

    metadata['media'].append(media)

    jsonSave(metadata, paths['metadata']['path'])


    return
def metadataFormatted():
    """Format metadata to send."""

    def formattedValue(originalValue, excludeKeys):

        if isinstance(originalValue, dict):

            newValue = {}

            for originalKey in originalValue.keys():

                if not originalKey in excludeKeys:

                    newValue[originalKey] = formattedValue(originalValue[originalKey])

            return newValue
        
        elif isinstance(originalValue, list):

            newValue = []

            for originalListItem in originalValue:

                if isinstance(originalListItem, dict) or isinstance(originalListItem, list):

                    newValue.append(formattedValue(originalListItem))

                else:

                    newValue.append(originalListItem)

            return newValue


        return originalValue

    excludeKeys = ['path']

    from utils import jsonLoad

    metadata = jsonLoad(paths['metadata']['path'])

    formattedMetadata = formattedValue(metadata)


    return formattedMetadata


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
