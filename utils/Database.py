#!/usr/bin/python3.14
# -*- coding: utf-8 -*-


import sqlite3, sys


class Database:


    validation = {
        'media': {
            'allow_extra_keys': True,
            'type': {
                'required': True,
                'types': ['str'],
                'json_include': True,
                'extra': []
            },
            'parent': {
                'required': False,
                'types': ['str'],
                'json_include': True,
                'extra': []
            },
            'file': {
                'required': True,
                'types': ['str'],
                'json_include': True,
                'extra': ['stringLengthGreaterThanZero']
            },
            'path': {
                'required': True,
                'types': ['str'],
                'json_include': False,
                'extra': ['stringLengthGreaterThanZero']
            },
            'size': {
                'required': True,
                'types': ['int_list'],
                'json_include': True,
                'extra': ['listLengthIsTwo']
            },
            'bytes': {
                'required': True,
                'types': ['int'],
                'json_include': True,
                'extra': []
            },
            'uploaded': {
                'required': True,
                'types': ['int', 'float'],
                'json_include': True,
                'extra': []
            },
            'created': {
                'required': False,
                'types': ['int', 'float'],
                'json_include': True,
                'extra': []
            },
            'thumbnails': {
                'required': False,
                'types': ['media_list'],
                'json_include': True,
                'extra': []
            },
            'tags': {
                'required': False,
                'types': ['tag_list'],
                'json_include': True,
                'extra': []
            }
        },
        'tag': {
            'allow_extra_keys': False,
            'name': {
                'required': True,
                'types': ['str'],
                'json_include': True,
                'extra': ['stringLengthGreaterThanZero']
            }
        }
    }


    def __init__(self):
        """Initialize."""

        from utils import loggingGet, getPaths
        self.logger = loggingGet(str(self.__class__.__name__).lower())

        self.paths = getPaths()


        return


    def metadataGet(self, formatted=True):
        """Get metadata from db."""

        metadata = self._metadataLoad()

        if formatted == True:

            metadata = self._metadataFormatted(metadata)


        return metadata


    # Database queries
    def _dbGet(self, query, values=None, parentConnection=None, parentCursor=None, closeOnExit=True):
        """Get records from db."""

        if not isinstance(query, str):

            self.logger.error(' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), 'invalid query']))
            return

        if not values is None:

            if not isinstance(values, tuple) and not isinstance(values, list):

                self.logger.error(' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), 'invalid values']))
                return

            if isinstance(values, list):

                if not all([isinstance(value, tuple) for value in values]) == True:

                    self.logger.error(' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), 'invalid values']))
                    return

        try:

            dbConnection = parentConnection
            dbCursor = parentCursor

            if dbConnection is None:

                dbConnection = sqlite3.connect(
                    self.paths['database']['path'],
                    check_same_thread=False
                )

            if dbCursor is None: dbCursor = dbConnection.cursor()

            dbCursor.execute(query, values)

            results = [result for result in dbCursor.fetchall()]

            #dbConnection.commit()

            if closeOnExit == True:

                if not dbCursor is None: dbCursor.close()
                if not dbConnection is None: dbConnection.close()

            return results

        except Exception as e:

            self.logger.error(' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), repr(e)]))


        return
    def _dbModify(self, query, values, parentConnection=None, parentCursor=None, closeOnExit=True):
        """Add/modify/remove records from db."""

        if not isinstance(query, str):

            self.logger.error(' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), 'invalid query']))
            return

        if not values is None:

            if not isinstance(values, tuple) and not isinstance(values, list):

                self.logger.error(' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), 'invalid values']))
                return

            if isinstance(values, list):

                if not all([isinstance(value, tuple) for value in values]) == True:

                    self.logger.error(' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), 'invalid values']))
                    return

        try:

            dbConnection = parentConnection
            dbCursor = parentCursor

            if dbConnection is None:

                dbConnection = sqlite3.connect(
                    self.paths['database']['path'],
                    check_same_thread=False
                )

            if dbCursor is None: dbCursor = dbConnection.cursor()

            if isinstance(values, tuple):

                dbCursor.execute(query, values)

            elif isinstance(values, list):

                for tupleValues in values:

                    self._dbModify(
                        query,
                        tupleValues,
                        parentConnection=dbConnection,
                        parentCursor=dbCursor,
                        closeOnExit=False
                    )

            dbConnection.commit()

            if closeOnExit == True:

                if not dbCursor is None: dbCursor.close()
                if not dbConnection is None: dbConnection.close()

        except Exception as e:

            self.logger.error(' '.join([str(self.__class__.__name__), str(sys._getframe().f_code.co_name), repr(e)]))


        return


    # Media
    def _mediaValidate(self, media):
        """Validate media."""

        if isinstance(media, dict):

            return self._validItem('media', media)
        
        elif isinstance(media, list):

            if len(media) > 0:

                return all([self._validItem('media', mediaItem) for mediaItem in media]) == True

            else:

                return True


        return False
    def _mediaGet(self, media=None):
        """Get media from db."""

        def dbResultsToMedias(results):

            def dbResultToMedia(result):

                mediaResult = {
                    'type': result[0],
                    'file': result[2],
                    'path': result[3],
                    'size': json.loads(result[4]),
                    'bytes': result[5],
                    'uploaded': result[6],
                    'created': result[7]
                }

                if mediaResult['type'] == 'original':

                    mediaResult['tags'] = json.loads(result[8])
                    mediaResult['thumbnails'] = []

                elif mediaResult['type'] == 'thumbnail':

                    mediaResult['parent'] = result[1]


                return mediaResult

            import json

            mediaResults = []
            thumbnailResults = []

            for result in results:

                mediaResult = dbResultToMedia(result)

                if mediaResult['type'] == 'original':

                    mediaResults.append(mediaResult)

                elif mediaResult['type'] == 'thumbnail':

                    thumbnailResults.append(mediaResult)

            for m in range(len(mediaResults)):

                for t in range(len(thumbnailResults)):

                    if mediaResults[m]['file'] == thumbnailResults[t]['parent']:

                        mediaResults[m]['thumbnails'].append(thumbnailResults[t])

            del thumbnailResults
            del results


            return mediaResults

        if media is None:

            return dbResultsToMedias(
                self._dbGet(
                    'SELECT type, parent, file, path, size, bytes, uploaded, created, tags FROM media;',
                    closeOnExit=True
                )
            )

        else:

            if 'file' in media.keys():

                return dbResultsToMedias(
                    self._dbGet(
                        'SELECT type, parent, file, path, size, bytes, uploaded, created, tags FROM media WHERE file = ? OR parent = ?;',
                        values=(
                            media['file'],
                            media['file']
                        ),
                        closeOnExit=True
                    )
                )


        return
    def _mediaToDbValues(self, media, updating=False):
        """Media dict to db values tuple."""

        import json

        values = tuple()

        if media['type'] == 'original':

            if updating == False:

                values = tuple(
                    [
                        media['type'],
                        None,
                        media['file'],
                        media['path'],
                        json.dumps(media['size']),
                        media['bytes'],
                        media['uploaded'],
                        media['created'],
                        json.dumps(media['tags'])
                    ]
                )

            else:

                values = tuple(
                    [
                        media['type'],
                        None,
                        media['path'],
                        json.dumps(media['size']),
                        media['bytes'],
                        media['uploaded'],
                        media['created'],
                        json.dumps(media['tags']),
                        media['file']
                    ]
                )

            if 'thumbnails' in media.keys():

                if len(media['thumbnails']) > 0:

                    values = [values]

                    for thumbnail in media['thumbnails']:

                        values.append(self._mediaToDbValues(thumbnail, updating))

        elif media['type'] == 'thumbnail':

            if updating == False:

                values = tuple(
                    [
                        media['type'],
                        media['parent'],
                        media['file'],
                        media['path'],
                        json.dumps(media['size']),
                        media['bytes'],
                        media['uploaded'],
                        media['created'],
                        None
                    ]
                )

            else:

                values = tuple(
                    [
                        media['type'],
                        media['parent'],
                        media['path'],
                        json.dumps(media['size']),
                        media['bytes'],
                        media['uploaded'],
                        media['created'],
                        None,
                        media['file']
                    ]
                )


        return values
    def _mediaAdd(self, media):
        """Add new media."""

        self._dbModify(
            'INSERT INTO media (type, parent, file, path, size, bytes, uploaded, created, tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);',
            values=self._mediaToDbValues(media, False),
            closeOnExit=True
        )


        return
    def _mediaUpdate(self, media):
        """Add new media."""

        self._dbModify(
            'UPDATE media SET type = ?, parent = ?, path = ?, size = ?, bytes = ?, uploaded = ?, created = ?, tags = ? WHERE file = ?;',
            values=self._mediaToDbValues(media, True),
            closeOnExit=True
        )


        return
    def _mediaDelete(self, media):
        """Add new media."""

        import os

        os.remove(media['path'])

        for thumbnail in media['thumbnails']:

            os.remove(thumbnail['path'])

        self._dbModify(
            'DELETE FROM media WHERE file = ? OR parent = ?;',
            values=tuple(
                [
                    media['file'],
                    media['file']
                ]
            ),
            closeOnExit=True
        )


        return

    # Playlist
    def _playlistGenerate(self):
        """."""


        return
    def _playlistFilter(self, originalPlaylist):
        """."""


        return originalPlaylist
    def _playlistSort(self, originalPlaylist):
        """."""


        return originalPlaylist
    def _playlistGet(self):
        """."""


        return
    def _playlistSave(self, playlist):
        """."""


        return

    # Metadata
    def _metadataFormatted(self, metadata=None):
        """Strip internal keys."""

        if metadata is None: metadata = self._metadataLoad()

        # TODO:


        return metadata
    def _metadataLoad(self):
        """Load metadata from db."""

        metadata = {
            'media': self._mediaGet(),
            'playlist': self._playlistGenerate(),
            'tags': []
        }

        for media in metadata['media']:

            if 'tags' in media.keys():

                for tag in media['tags']:

                    if not tag['name'] in metadata['tags']:

                        metadata['tags'].append(tag['name'])


        return metadata
    def _metadataSave(self, metadata):
        """Save metadata to db."""

        self._mediaUpdate(metadata['media'])
        self._playlistSave(metadata['playlist'])


        return
    
    # Validation
    def _validItem(self, itemType, item):
        """Validate an item."""

        if not isinstance(item, dict):

            return False

        if len(item.keys()) == 0:

            return False

        if itemType in self.validation.keys():

            for validationKey in self.validation[itemType].keys():

                if isinstance(self.validation[itemType][validationKey], dict):

                    if validationKey in item.keys():

                        if len(self.validation[itemType][validationKey]['types']) > 0:

                            typeValidations = []

                            for validType in self.validation[itemType][validationKey]['types']:

                                if validType == 'str':

                                    typeValidations.append(isinstance(item[validationKey], str))

                                elif validType == 'str_list':

                                    if isinstance(item[validationKey], list):

                                        if len(item[validationKey]) > 0:

                                            typeValidations.append(
                                                all(
                                                    [
                                                        isinstance(child, str)
                                                        for child in item[validationKey]
                                                    ]
                                                ) == True
                                            )

                                        else:

                                            typeValidations.append(True)

                                    else:

                                        typeValidations.append(False)

                                elif validType == 'bool':

                                    typeValidations.append(isinstance(item[validationKey], bool))

                                elif validType == 'bool_list':

                                    if isinstance(item[validationKey], list):

                                        if len(item[validationKey]) > 0:

                                            typeValidations.append(
                                                all(
                                                    [
                                                        isinstance(child, bool)
                                                        for child in item[validationKey]
                                                    ]
                                                ) == True
                                            )

                                        else:

                                            typeValidations.append(True)

                                    else:

                                        typeValidations.append(False)

                                elif validType == 'int':

                                    typeValidations.append(isinstance(item[validationKey], int))

                                elif validType == 'int_list':

                                    if isinstance(item[validationKey], list):

                                        if len(item[validationKey]) > 0:

                                            typeValidations.append(
                                                all(
                                                    [
                                                        isinstance(child, int)
                                                        for child in item[validationKey]
                                                    ]
                                                ) == True
                                            )

                                        else:

                                            typeValidations.append(True)

                                    else:

                                        typeValidations.append(False)

                                elif validType == 'float':

                                    typeValidations.append(isinstance(item[validationKey], float))

                                elif validType == 'float_list':

                                    if isinstance(item[validationKey], list):

                                        if len(item[validationKey]) > 0:

                                            typeValidations.append(
                                                all(
                                                    [
                                                        isinstance(child, float)
                                                        for child in item[validationKey]
                                                    ]
                                                ) == True
                                            )

                                        else:

                                            typeValidations.append(True)

                                    else:

                                        typeValidations.append(False)

                                else:

                                    for validationType in self.validation.keys():

                                        if validationType == validType:

                                            typeValidations.append(
                                                self._validItem(validType, item[validationKey])
                                            )

                                        elif len(validType.split('_')) == 2 and validationType == validType.split('_')[0] and validType.split('_')[-1] == 'list':

                                            if isinstance(item[validationKey], list):

                                                if len(item[validationKey]) > 0:

                                                    typeValidations.append(
                                                        all(
                                                            [
                                                                self._validItem(validationType, child)
                                                                for child in item[validationKey]
                                                            ]
                                                        ) == True
                                                    )

                                                else:

                                                    typeValidations.append(True)

                                            else:

                                                typeValidations.append(False)

                            if not any(typeValidations) == True:

                                return False

                        if len(self.validation[itemType][validationKey]['extra']) > 0:

                            extraValidations = []

                            for extraName in self.validation[itemType][validationKey]['extra']:

                                extraMethod = getattr(self, extraName)

                                if not extraMethod is None:

                                    extraValidations.append(
                                        extraMethod(item[validationKey])
                                    )

                            if not any(extraValidations) == True:

                                return False

                    else:

                        if self.validation[itemType][validationKey]['required'] == True:

                            return False

            if self.validation[itemType]['allow_extra_keys'] == False:

                if any([itemKey not in self.validation[itemType].keys() for itemKey in item.keys()]) == True:

                    return False


        return True
    def stringLengthGreaterThanZero(self, value):
        return True if len(value) > 0 else False
    def listLengthIsTwo(self, value):
        return True if len(value) == 2 else False
