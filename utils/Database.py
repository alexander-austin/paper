#!/usr/bin/python3.14
# -*- coding: utf-8 -*-


import sqlite3, sys

class Database:


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
                    self.paths['db']['path'],
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
                    self.paths['db']['path'],
                    check_same_thread=False
                )

            if dbCursor is None: dbCursor = dbConnection.cursor()

            dbCursor.execute(query, values)

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


        return False
    def _mediaGet(self, media=None):
        """Get media from db."""


        return False
    def _mediaAdd(self, media):
        """Add new media."""


        return False
    def _mediaUpdate(self, media):
        """Add new media."""


        return False
    def _mediaDelete(self, media):
        """Add new media."""


        return False

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
    def _loadPlaylist(self):
        """."""


        return
    def _savePlaylist(self):
        """."""


        return

    # Metadata
    def _metadataFormatted(self, metadata=None):
        """Strip internal keys."""

        if metadata is None: metadata = self._metadataLoad()


        return metadata
    def _metadataLoad(self):
        """Load metadata from db."""


        return
    def _metadataSave(self):
        """Save metadata to db."""


        return
