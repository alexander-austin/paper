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
        },
        'sort': {
            'allow_extra_keys': False,
            'priority': {
                'required': True,
                'types': ['int'],
                'json_include': True,
                'extra': ['intGreaterThanOrEqualToZero']
            },
            'key': {
                'required': True,
                'types': ['str'],
                'json_include': True,
                'extra': ['stringLengthGreaterThanZero']
            },
            'direction': {
                'required': True,
                'types': ['str'],
                'json_include': True,
                'extra': ['stringLengthGreaterThanZero', 'stringPlaylistSortDirection']
            }
        },
        'filter': {
            'allow_extra_keys': False,
            'priority': {
                'required': True,
                'types': ['int'],
                'json_include': True,
                'extra': ['intGreaterThanOrEqualToZero']
            },
            'key': {
                'required': True,
                'types': ['str'],
                'json_include': True,
                'extra': ['stringLengthGreaterThanZero']
            },
            'condition': {
                'required': True,
                'types': ['str'],
                'json_include': True,
                'extra': ['stringLengthGreaterThanZero']
            },
            'value': {
                'required': True,
                'types': ['str', 'bool', 'int', 'float', 'media', 'tag', 'str_list', 'bool_list', 'int_list', 'float_list', 'media_list', 'tag_list'],
                'json_include': True,
                'extra': []
            }
        },
        'playlist': {
            'allow_extra_keys': False,
            'active': {
                'required': True,
                'types': ['bool'],
                'json_include': True,
                'extra': []
            },
            'name': {
                'required': True,
                'types': ['str'],
                'json_include': True,
                'extra': ['stringLengthGreaterThanZero']
            },
            'interval': {
                'required': True,
                'types': ['int', 'float'],
                'json_include': True,
                'extra': ['floatPlaylistInterval']
            },
            'mode': {
                'required': True,
                'types': ['str'],
                'json_include': True,
                'extra': ['stringLengthGreaterThanZero', 'stringPlaylistMode']
            },
            'sorts': {
                'required': False,
                'types': ['sort_list'],
                'json_include': True,
                'extra': []
            },
            'filters': {
                'required': False,
                'types': ['filter_list'],
                'json_include': True,
                'extra': []
            },
            'index': {
                'required': True,
                'types': ['int'],
                'json_include': True,
                'extra': ['intGreaterThanOrEqualToZero']
            },
            'files': {
                'required': True,
                'types': ['str_list'],
                'json_include': True,
                'extra': ['listLengthGreaterThanZero']
            }
        },
        'metadata': {
            'allow_extra_keys': False,
            'media': {
                'required': True,
                'types': ['media_list'],
                'json_include': True,
                'extra': []
            },
            'playlists': {
                'required': False,
                'types': ['playlist_list'],
                'json_include': True,
                'extra': []
            },
            'tags': {
                'required': False,
                'types': ['str_list'],
                'json_include': True,
                'extra': []
            }
        },
        'state': {
            'allow_extra_keys': True,
            'timestamp': {
                'required': True,
                'types': ['int', 'float'],
                'json_include': True,
                'extra': []
            },
            'component': {
                'required': True,
                'types': ['str'],
                'json_include': True,
                'extra': ['stringLengthGreaterThanZero']
            },
            'type': {
                'required': True,
                'types': ['str'],
                'json_include': True,
                'extra': ['stringLengthGreaterThanZero']
            },
            'value': {
                'required': True,
                'types': ['str'],
                'json_include': True,
                'extra': ['stringLengthGreaterThanZero']
            },
            'pending': {
                'required': True,
                'types': ['bool'],
                'json_include': True,
                'extra': []
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

            metadata = self._itemToJson(metadata)


        return metadata
    def metadataMediaFileExists(self, fileName):
        """Check if file exists on disk or in DB."""

        import os

        media = self._mediaGet()

        for m in range(len(media)):

            if media[m]['file'] == fileName:

                if os.path.exists(media[m]['path']):

                    return media[m]

            for t in range(len(media[m]['thumbnails'])):

                if media[m]['thumbnails'][t]['file'] == fileName:

                    if os.path.exists(media[m]['thumbnails'][t]['path']):

                        return media[m]['thumbnails'][t]

        if os.path.exists(os.path.join(self.paths['media']['path'], fileName)):

            return True

        if os.path.exists(os.path.join(self.paths['temp']['path'], fileName)):

            return True


        return False
    def metadataMediaAdd(self, media):
        """Add media to db."""

        if self._validItem('media', media) == True:

            existingMedia = self.metadataFileExists(media['file'])

            if isinstance(existingMedia, bool) and existingMedia == False:

                self._mediaAdd(media)


        return
    def metadataMediaUpdate(self, media):
        """Update media in db."""

        if self._validItem('media', media) == True:

            existingMedia = self.metadataFileExists(media['file'])

            if isinstance(existingMedia, bool) and existingMedia == False:

                self._mediaUpdate(media)


        return
    def metadataMediaDelete(self, media):
        """Delete media from db."""

        if self._validItem('media', media) == True:

            existingMedia = self.metadataFileExists(media['file'])

            if isinstance(existingMedia, bool) and existingMedia == False:

                self._mediaDelete(media)


        return

    def stateGet(self, stateType='event', formatted=True):
        """Get state from db."""

        state = self._stateGet(
            onlyType=stateType,
            onlyPending=False if stateType == 'event' else True
        )

        if formatted == True:

            state = '[%(values)s]' % {
                'values': ', '.join(
                    [
                        self._itemToJson('state', s)
                        for s in state
                    ]
                )
            }


        return state
    def stateAdd(self, state):
        """Add state to db."""

        if self._validItem('state', state) == True:

            self._stateAdd(state)


        return
    def stateUpdate(self, state):
        """Update state in db."""

        if self._validItem('state', state) == True:

            self._stateUpdate(state)


        return
    def stateDelete(self, state):
        """Delete state from db."""

        if self._validItem('state', state) == True:

            self._stateDelete(state)


        return

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

                import json

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
                    'SELECT type, parent, file, path, size, bytes, uploaded, created, tags FROM media ORDER BY uploaded DESC;',
                    closeOnExit=True
                )
            )

        else:

            if 'file' in media.keys():

                return dbResultsToMedias(
                    self._dbGet(
                        'SELECT type, parent, file, path, size, bytes, uploaded, created, tags FROM media WHERE file = ? OR parent = ? ORDER BY uploaded DESC;',
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
            values=[self._mediaToDbValues(m, False) for m in media] if isinstance(media, list) else self._mediaToDbValues(media, False),
            closeOnExit=True
        )


        return
    def _mediaUpdate(self, media):
        """Update existing media."""

        self._dbModify(
            'UPDATE media SET type = ?, parent = ?, path = ?, size = ?, bytes = ?, uploaded = ?, created = ?, tags = ? WHERE file = ?;',
            values=[self._mediaToDbValues(m, True) for m in media] if isinstance(media, list) else self._mediaToDbValues(media, True),
            closeOnExit=True
        )


        return
    def _mediaDelete(self, media):
        """Delete existing media."""

        import os

        if isinstance(media, dict): media = [media]

        if isinstance(media, list):

            for m in media:

                os.remove(m['path'])

                for thumbnail in m['thumbnails']:

                    os.remove(thumbnail['path'])

        else:

            os.remove(media['path'])

            for thumbnail in media['thumbnails']:

                os.remove(thumbnail['path'])

        self._dbModify(
            'DELETE FROM media WHERE file = ? OR parent = ?;',
            values=[tuple([m['file'], m['file']]) for m in media] if isinstance(media, list) else tuple([media['file'], media['file']]),
            closeOnExit=True
        )


        return

    # Playlist
    def _playlistPopulate(self, name, interval=30.0, mode='shuffle', sorts=[], filters=[], media=None, save=True):
        """Add new playlist or update existing."""

        def filterPass(value, filterCondition, filterValue):

            if filterCondition == 'equal':

                if value == filterValue: return True

            elif filterCondition == 'not equal':

                if not value == filterValue: return True

            elif filterCondition == 'in':

                if value in filterValue: return True

            elif filterCondition == 'not in':

                if not value in filterValue: return True

            elif filterCondition == 'greater than':

                if value > filterValue: return True

            elif filterCondition == 'greater than or equal':

                if value >= filterValue: return True

            elif filterCondition == 'less than':

                if value < filterValue: return True

            elif filterCondition == 'less than or equal':

                if value <= filterValue: return True

            elif filterCondition == 'between':

                if value > filterValue[0] and value < filterValue[1]: return True

            elif filterCondition == 'between or equal':

                if value >= filterValue[0] and value <= filterValue[1]: return True


            return False

        if media is None:

            media = self._mediaGet()

        playlist = {
            'name': name,
            'interval': interval,
            'mode': mode,
            'sorts': sorts,
            'filters': filters,
            'index': 0,
            'files': []
        }

        if isinstance(media, list):

            if len(media) > 0:

                filteredMedia = []

                # Filter
                for m in range(len(media)):

                    if len(playlist['filters']) > 0:

                        passFilter = []

                        for filter in sorted(playlist['filters'], lambda f: f['priority']):

                            if filter['key'] == 'uploaded':

                                passFilter.append(filterPass(media[m]['uploaded'], filter['condition'], filter['value']))

                            elif filter['key'] == 'created':

                                passFilter.append(filterPass(media[m]['created'], filter['condition'], filter['value']))

                            elif filter['key'] == 'tags':

                                passFilter.append(all([filterPass(tag['name'], filter['condition'], filter['value']) for tag in media[m]['tags']]) == True)

                        if all(passFilter) == True:

                            filteredMedia.append(media[m])

                    else:

                        filteredMedia.append(media[m])

                # Sort
                if len(filteredMedia) > 0:

                    if len(playlist['sorts']) > 0:

                        for sorter in sorted(playlist['sorts'], lambda s: s['priority']):

                            filteredMedia = sorted(
                                filteredMedia,
                                lambda fm: fm[sorter['key']],
                                reverse=False if sorter['direction'] == 'ASC' else True
                            )

                playlist['files'] = filteredMedia

        if save == True:

            self._playlistAdd(playlist)


        return playlist
    def _playlistsPopulate(self, save=True):
        """Populate files of all playlists."""

        media = self._mediaGet()
        playlists = self._playlistGet()

        for p in range(len(playlists)):

            playlists[p] = self._playlistPopulate(
                playlists[p]['name'],
                playlists[p]['interval'],
                playlists[p]['mode'],
                playlists[p]['sorts'],
                playlists[p]['filters'],
                media=media,
                save=False
            )

        if save == True:

            self._playlistUpdate(playlists)


        return playlists

    def _playlistGet(self, playlist=None):
        """Get playlist from db."""

        def dbResultsToPlaylists(results):

            def dbResultToPlaylist(result):

                import json

                playlistResult = {
                    'active': True if result[0] == 1 else False,
                    'name': result[1],
                    'interval': result[2],
                    'mode': result[3],
                    'filters': json.loads(result[4]),
                    'sorts': json.loads(result[5]),
                    'index': result[6],
                    'files': json.loads(result[7])
                }


                return playlistResult

            playlistResults = []

            for result in results:

                playlistResults.append(
                    dbResultToPlaylist(result)
                )

            del results


            return playlistResults

        if playlist is None:

            return dbResultsToPlaylists(
                self._dbGet(
                    'SELECT active, name, interval, mode, filters, sorts, [index], files FROM playlist ORDER BY name ASC;',
                    closeOnExit=True
                )
            )

        else:

            if 'name' in playlist.keys():

                return dbResultsToPlaylists(
                    self._dbGet(
                        'SELECT active, name, interval, mode, filters, sorts, [index], files FROM playlist WHERE name = ? ORDER BY name ASC;',
                        values=(
                            playlist['name'],
                        ),
                        closeOnExit=True
                    )
                )


        return
    def _playlistToDbValues(self, playlist, updating=False):
        """Playlist dict to db values tuple."""

        import json

        values = tuple()

        if updating == False:

            values = tuple(
                [
                    1 if playlist['active'] == True else 0,
                    playlist['name'],
                    float(playlist['interval']),
                    playlist['mode'],
                    json.dumps(playlist['filters']) if 'filters' in playlist.keys() else None,
                    json.dumps(playlist['sorts']) if 'sorts' in playlist.keys() else None,
                    playlist['index'],
                    json.dumps(playlist['files']) if 'files' in playlist.keys() else None
                ]
            )

        else:

            values = tuple(
                [
                    1 if playlist['active'] == True else 0,
                    float(playlist['interval']),
                    playlist['mode'],
                    json.dumps(playlist['filters']) if 'filters' in playlist.keys() else None,
                    json.dumps(playlist['sorts']) if 'sorts' in playlist.keys() else None,
                    playlist['index'],
                    json.dumps(playlist['files']) if 'files' in playlist.keys() else None,
                    playlist['name']
                ]
            )


        return values
    def _playlistAdd(self, playlist):
        """Add new playlist."""

        self._dbModify(
            'INSERT INTO playlist (active, name, interval, mode, filters, sorts, [index], files) VALUES (?, ?, ?, ?, ?, ?, ?, ?);',
            values=[self._playlistToDbValues(p, False) for p in playlist] if isinstance(playlist, list) else self._playlistToDbValues(playlist, False),
            closeOnExit=True
        )


        return
    def _playlistUpdate(self, playlist):
        """Update existing playlist."""

        self._dbModify(
            'UPDATE playlist SET active = ?, interval = ?, mode = ?, filters = ?, sorts = ?, [index] = ?, files = ? WHERE name = ?;',
            values=[self._playlistToDbValues(p, True) for p in playlist] if isinstance(playlist, list) else self._playlistToDbValues(playlist, True),
            closeOnExit=True
        )


        return
    def _playlistDelete(self, playlist):
        """Delete existing playlist."""

        self._dbModify(
            'DELETE FROM playlist WHERE name = ?;',
            values=[tuple([p['name'], ]) for p in playlist] if isinstance(playlist, list) else tuple([playlist['name'], ]),
            closeOnExit=True
        )


        return

    # Metadata
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

    # State
    def _stateGet(self, onlyType=None, onlyPending=False):
        """Get state from db."""

        def dbResultsToStates(results):

            def dbResultToState(result):

                import json

                stateResult = {
                    'timestamp': float(result[0]),
                    'component': result[1],
                    'type': result[2],
                    'value': json.loads(result[3]),
                    'pending': True if result[4] == 1 else False
                }


                return stateResult

            stateResults = []

            for result in results:

                stateResults.append(
                    dbResultToState(result)
                )

            del results


            return stateResults

        if isinstance(onlyType, str):

            if onlyType in ['state', 'event']:

                if onlyPending == True:

                    return dbResultsToStates(
                        self._dbGet(
                            'SELECT timestamp, component, type, value, pending FROM state WHERE type = ? AND pending = 1 ORDER BY timestamp DESC;',
                            values=(
                                onlyType,
                            ),
                            closeOnExit=True
                        )
                    )

                else:

                    return dbResultsToStates(
                        self._dbGet(
                            'SELECT timestamp, component, type, value, pending FROM state WHERE type = ? ORDER BY timestamp DESC;',
                            values=(
                                onlyType,
                            ),
                            closeOnExit=True
                        )
                    )

        else:

            return dbResultsToStates(
                self._dbGet(
                    'SELECT timestamp, component, type, value, pending FROM state ORDER BY timestamp DESC;',
                    closeOnExit=True
                )
            )


        return []
    def _stateToDbValues(self, state, updating=False):
        """State dict to db values tuple."""

        import json

        values = tuple()

        if updating == False:

            values = tuple(
                [
                    float(state['timestamp']),
                    state['component'],
                    state['type'],
                    json.dumps(state['value']),
                    1 if state['pending'] == True else 0
                ]
            )

        else:

            values = tuple(
                [
                    json.dumps(state['value']),
                    1 if state['pending'] == True else 0,
                    float(state['timestamp']),
                    state['component'],
                    state['type']
                ]
            )


        return values
    def _stateAdd(self, state):
        """Add new state."""

        self._dbModify(
            'INSERT INTO state (timestamp, component, type, value, pending) VALUES (?, ?, ?, ?, ?);',
            values=[self._stateToDbValues(s, False) for s in state] if isinstance(state, list) else self._stateToDbValues(state, False),
            closeOnExit=True
        )


        return
    def _stateUpdate(self, state):
        """Update existing state."""

        self._dbModify(
            'UPDATE state SET value = ?, pending = ? WHERE timestamp = ? AND component = ? AND type = ?;',
            values=[self._stateToDbValues(s, True) for s in state] if isinstance(state, list) else self._stateToDbValues(state, True),
            closeOnExit=True
        )


        return
    def _stateDelete(self, state):
        """Delete existing playlist."""

        self._dbModify(
            'DELETE FROM state WHERE timestamp = ? AND component = ? AND type = ?;',
            values=[tuple([s['timestamp'], s['component'], s['type']]) for s in state] if isinstance(state, list) else tuple([state['timestamp'], state['component'], state['type']]),
            closeOnExit=True
        )


        return

    # Validation
    def _itemToJson(self, itemType, item):
        """Item to JSON."""

        def valueToJsonKV(key, value, required, validTypes):

            if value is None:

                if required == True:

                    return '"%(key)s": null' % {
                        'key': key
                    }

            else:

                if isinstance(value, str):

                    if 'str' in validTypes:

                        return '"%(key)s": "%(value)s"' % {
                            'key': key,
                            'value': value
                        }

                elif isinstance(value, bool):

                    if 'bool' in validTypes:

                        return '"%(key)s": %(value)s' % {
                            'key': key,
                            'value': 'trus' if value == True else 'false'
                        }

                elif isinstance(value, int):

                    if 'int' in validTypes:

                        return '"%(key)s": %(value)d' % {
                            'key': key,
                            'value': value
                        }

                elif isinstance(value, float):

                    if 'float' in validTypes:

                        return '"%(key)s": %(value)f' % {
                            'key': key,
                            'value': value
                        }

                elif isinstance(value, list):

                    if len(value) > 0:

                        if all([isinstance(v, str) for v in value]) == True:

                            if 'str_list' in validTypes:

                                return '"%(key)s": [%(values)s]' % {
                                    'key': key,
                                    'values': ', '.join(
                                        [
                                            '"%s"' % (v, )
                                            for v in value
                                        ]
                                    )
                                }

                        elif all([isinstance(v, bool) for v in value]) == True:

                            if 'bool_list' in validTypes:

                                return '"%(key)s": [%(values)s]' % {
                                    'key': key,
                                    'values': ', '.join(
                                        [
                                            'true' if v == True else 'false'
                                            for v in value
                                        ]
                                    )
                                }

                        elif all([isinstance(v, int) for v in value]) == True:

                            if 'int_list' in validTypes:

                                return '"%(key)s": [%(values)s]' % {
                                    'key': key,
                                    'values': ', '.join(
                                        [
                                            '%d' % (v, )
                                            for v in value
                                        ]
                                    )
                                }

                        elif all([isinstance(v, float) for v in value]) == True:

                            if 'float_list' in validTypes:

                                return '"%(key)s": [%(values)s]' % {
                                    'key': key,
                                    'values': ', '.join(
                                        [
                                            '%f' % (v, )
                                            for v in value
                                        ]
                                    )
                                }

                        elif all([isinstance(v, dict) for v in value]) == True:

                            for validType in validTypes:

                                if len(validType.split('_')) == 2:

                                    if validType.split('_')[-1] == 'list' and validType.split('_')[0] in self.validation.keys():

                                        if all([self._validItem(validType, v) == True for v in value]) == True:

                                            return '"%(key)s": [%(values)s]' % {
                                                'key': key,
                                                'values': ', '.join(
                                                    [
                                                        self._itemToJson(validType, v)
                                                        for v in value
                                                    ]
                                                )
                                            }

                    else:

                        if required == True:

                            return '"%(key)s": []' % {
                                'key': key
                            }

                elif isinstance(value, dict):

                    for validType in validTypes:

                        if validType in self.validation.keys():

                            if self._validItem(validType, value) == True:

                                return '"%(key)s": %(value)s' % {
                                    'key': key,
                                    'value': self._itemToJson(validType, value)
                                }


            return None

        if not isinstance(item, dict):

            if isinstance(item, list):

                return '[%(items)s]' % {
                    'items': ', '.join(
                        [
                            self._itemToJson(itemType, i)
                            for i in item
                        ]
                    )
                }

            else:

                return False

        if len(item.keys()) == 0:

            return False

        if itemType in self.validation.keys():

            kvPairs = []

            for validationKey in self.validation[itemType].keys():

                if isinstance(self.validation[itemType][validationKey], dict):

                    if validationKey in item.keys() and self.validation[itemType][validationKey]['json_include'] == True:

                        kv = valueToJsonKV(
                            validationKey,
                            item[validationKey],
                            self.validation[itemType][validationKey]['required'],
                            self.validation[itemType][validationKey]['types']
                        )

                        if not kv is None:

                            kvPairs.append(kv)

            if len(kvPairs) > 0:

                return '{%(kv_pairs)s}' % {
                    'kv_pairs': ', '.join(kvPairs)
                }


        return ''
    def _validItem(self, itemType, item):
        """Validate an item."""

        if not isinstance(item, dict):

            if isinstance(item, list):

                return all(
                    [
                        self._validItem(itemType, i)
                        for i in item
                    ]
                )

            else:

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
    def floatPlaylistInterval(self, value):
        return True if (value == 0 or value >= 7.5) else False
    def stringPlaylistSortDirection(self, value):
        return True if value in ['ASC', 'DESC'] else False
    def stringPlaylistFilterCondition(self, value):
        return True if value in ['equal', 'not equal', 'in', 'not in', 'greater than', 'greater than or equal', 'less than', 'less than or equal', 'between', 'between or equal'] else False
    def stringPlaylistMode(self, value):
        return True if value in ['shuffle', 'sequential'] else False
    def intGreaterThanOrEqualToZero(self, value):
        return True if value >= 0 else False
    def listLengthGreaterThanZero(self, value):
        return True if len(value) > 0 else False
    def listLengthIsTwo(self, value):
        return True if len(value) == 2 else False
