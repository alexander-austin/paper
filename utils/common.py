#!/usr/bin/python3.14
# -*- coding: utf-8 -*-


# Paths
def getPaths():
    """Get file paths, create directories if needed."""

    import os

    paths = {
        'root': {
            'type': 'directory',
            'publish': False,
            'path': os.path.dirname(
                os.path.dirname(
                    os.path.realpath(__file__)
                )
            )
        },
        'data': {
            'type': 'directory',
            'publish': False,
            'path': os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    )
                ),
                'data'
            )
        },
        'temp': {
            'type': 'directory',
            'publish': False,
            'path': os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    )
                ),
                'temp'
            )
        },
        'web': {
            'type': 'directory',
            'publish': False,
            'path': os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    )
                ),
                'web'
            )
        },
        'root': {
            'type': 'directory',
            'publish': True,
            'path': os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    )
                ),
                'web',
                'root'
            )
        },
        'static': {
            'type': 'directory',
            'publish': True,
            'path': os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    )
                ),
                'web',
                'static'
            )
        },
        'media': {
            'type': 'directory',
            'publish': False,
            'path': os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    )
                ),
                'web',
                'media'
            )
        },
        'templates': {
            'type': 'directory',
            'publish': False,
            'path': os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    )
                ),
                'web',
                'templates'
            )
        },
        'database': {
            'type': 'db',
            'publish': False,
            'path': os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    )
                ),
                'data',
                'paper.db'
            )
        },
        'io_settings': {
            'type': 'json',
            'publish': False,
            'path': os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    )
                ),
                'data',
                'io_settings.json'
            )
        },
        'api_settings': {
            'type': 'json',
            'publish': False,
            'path': os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    )
                ),
                'data',
                'api_settings.json'
            )
        },
        'log_config': {
            'type': 'data',
            'publish': False,
            'path': os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    )
                ),
                'data',
                'logging.json'
            )
        },
        'database_log': {
            'type': 'log',
            'publish': False,
            'path': os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    )
                ),
                'data',
                'database.log'
            )
        },
        'display_log': {
            'type': 'log',
            'publish': False,
            'path': os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    )
                ),
                'data',
                'display.log'
            )
        },
        'gpinput_log': {
            'type': 'log',
            'publish': False,
            'path': os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    )
                ),
                'data',
                'gpinput.log'
            )
        },
        'imager_log': {
            'type': 'log',
            'publish': False,
            'path': os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    )
                ),
                'data',
                'imager.log'
            )
        },
        'mpu6050_log': {
            'type': 'log',
            'publish': False,
            'path': os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    )
                ),
                'data',
                'mpu6050.log'
            )
        },
        'font_mono_bold': {
            'type': 'font',
            'publish': False,
            'path': os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    )
                ),
                'web',
                'static',
                'fonts',
                'SplineSansMono-Bold.ttf'
            )
        }
    }

    for pathKey in paths.keys():

        paths[pathKey]['path'] = paths[pathKey]['path'].replace('/', os.path.sep).replace('\\', os.path.sep)

        if paths[pathKey]['type'] == 'directory':

            os.makedirs(paths[pathKey]['path'], exist_ok=True)


    return paths

# Logging
def loggingInit():
    """Initializes logging config."""

    import logging, logging.config, os, sys

    paths = getPaths()
    if not os.path.exists(paths['log_config']['path']): sys.exit('could not set logging, config path missing')

    loggingDictConfig = jsonLoad(paths['log_config']['path'])
    if loggingDictConfig is None: sys.exit('could not set logging, empty config data')

    if isinstance(loggingDictConfig, dict):

        if 'handlers' in loggingDictConfig.keys():

            if isinstance(loggingDictConfig['handlers'], dict):

                for handlerKey in loggingDictConfig['handlers'].keys():

                    for pathKey in paths.keys():

                        if paths[pathKey]['type'] == 'log':

                            if handlerKey.split('_')[0] == pathKey.split('_')[0]:

                                loggingDictConfig['handlers'][handlerKey]['filename'] = paths[pathKey]['path']
                                break

            else: sys.exit('could not set logging, config data improperly formatted')

        else: sys.exit('could not set logging, config data improperly formatted')

    else: sys.exit('could not set logging, config data improperly formatted')

    logging.config.dictConfig(loggingDictConfig)


    return
def loggingGet(loggerName):
    """Gets logger by name."""

    import logging

    loggingInit()


    return logging.getLogger(loggerName)

# File I/O
def jsonLoad(path, logger=None):
    """Load json data from file."""

    import json, logging, os, sys

    errorMessage = ''

    if isinstance(path, str):

        if os.path.exists(path):

            try:

                with open(path) as f:

                    try:
                        data = json.load(f)
                        return data
                    except Exception as e: errorMessage = '.'.join([str(__name__), str(sys._getframe().f_code.co_name), repr(e)])

            except FileNotFoundError: errorMessage = '.'.join([str(__name__), str(sys._getframe().f_code.co_name), 'path does not exist ' + path])
            except OSError: errorMessage = '.'.join([str(__name__), str(sys._getframe().f_code.co_name), 'OS error'])
            except Exception as e: errorMessage = '.'.join([str(__name__), str(sys._getframe().f_code.co_name), repr(e)])

        else: errorMessage = '.'.join([str(__name__), str(sys._getframe().f_code.co_name), 'path does not exist ' + path])

    else: errorMessage = '.'.join([str(__name__), str(sys._getframe().f_code.co_name), 'invalid path type ' + path])

    if len(errorMessage) == 0:
        errorMessage = None
    else:
        if isinstance(logger, logging.Handler): logger.warning(errorMessage)
        else: print(errorMessage)


    return errorMessage
def jsonSave(data, path, logger=None):
    """Save json data to file."""

    import json, logging, sys

    errorMessage = ''

    if isinstance(path, str):

        try:

            with open(path, 'w', encoding='utf-8') as f:

                f.write(json.dumps(data))

        except FileNotFoundError: errorMessage = ' '.join([str(__name__), str(sys._getframe().f_code.co_name), 'path does not exist'])
        except OSError: errorMessage = ' '.join([str(__name__), str(sys._getframe().f_code.co_name), 'OS error'])
        except Exception as e: errorMessage = ' '.join([str(__name__), str(sys._getframe().f_code.co_name), repr(e)])

    if len(errorMessage) == 0:
        errorMessage = None
    else:
        if isinstance(logger, logging.Handler): logger.warning(errorMessage)
        else: print(errorMessage)


    return errorMessage

# Time
def timestampEpoch():
    """Get current utc epoch timestamp."""
    from datetime import datetime, timezone
    return float((datetime.now(timezone.utc) - datetime.fromtimestamp(0, timezone.utc)).total_seconds())
def timestampString():
    """Current time string format."""
    from datetime import datetime, timezone
    return str(datetime.now(timezone.utc).strftime('%Y/%m/%d %H:%M:%S.%f'))[0:-3]
def timestampToString(epochTimestamp):
    """Existing time to string format."""
    from datetime import datetime, timezone
    if not isinstance(epochTimestamp, int) and not isinstance(epochTimestamp, float): return ''
    return str(datetime.fromtimestamp(epochTimestamp, tz=timezone.utc).strftime('%Y/%m/%d %H:%M:%S.%f'))[0:-3]
def timestampDelta(pastTimestamp):
    return timestampEpoch() - pastTimestamp

# First run setup
def setup():
    """Checks if necessary first run tasks have been completed and, if not, completes them."""

    def setupDatabase(paths, ioSettings):

        try:

            import os, sqlite3

            # Create database if missing
            if not os.path.exists(paths['database']['path']):

                print('creating database...')

                dbConnection = sqlite3.connect(
                    paths['database']['path'],
                    check_same_thread=False
                )
                dbCursor = dbConnection.cursor()

                dbCursor.execute(
                    """
                    CREATE TABLE media (
                        type     TEXT    NOT NULL ON CONFLICT ROLLBACK CHECK (type = 'original' OR type = 'thumbnail'),
                        parent   TEXT,
                        file     TEXT    NOT NULL ON CONFLICT ROLLBACK UNIQUE ON CONFLICT ROLLBACK,
                        path     TEXT    UNIQUE ON CONFLICT ROLLBACK NOT NULL ON CONFLICT ROLLBACK,
                        size     TEXT    NOT NULL ON CONFLICT ROLLBACK,
                        bytes    INTEGER NOT NULL ON CONFLICT ROLLBACK,
                        uploaded REAL    NOT NULL ON CONFLICT ROLLBACK,
                        created  REAL,
                        tags     TEXT
                    );
                    """
                )
                dbConnection.commit()

                dbCursor.execute(
                    """
                    CREATE TABLE playlist (
                        active   INTEGER NOT NULL ON CONFLICT ROLLBACK DEFAULT (0)  CHECK (active = 0 OR active = 1),
                        name     TEXT    NOT NULL ON CONFLICT ROLLBACK UNIQUE ON CONFLICT ROLLBACK,
                        interval REAL    NOT NULL ON CONFLICT ROLLBACK DEFAULT (30.0),
                        mode     TEXT    NOT NULL ON CONFLICT ROLLBACK CHECK (mode = 'sequential' OR mode = 'shuffle'),
                        filters  TEXT,
                        sorts    TEXT,
                        [index]  INTEGER NOT NULL ON CONFLICT ROLLBACK DEFAULT (0),
                        files    TEXT
                    );
                    """
                )
                dbConnection.commit()

                dbCursor.execute(
                    """
                    CREATE TABLE state_event (
                        timestamp REAL    NOT NULL ON CONFLICT ROLLBACK,
                        component TEXT    NOT NULL ON CONFLICT ROLLBACK,
                        type      TEXT    NOT NULL ON CONFLICT ROLLBACK CHECK (type = 'event' OR type = 'state'),
                        value     TEXT    NOT NULL ON CONFLICT ROLLBACK,
                        pending   INTEGER NOT NULL ON CONFLICT ROLLBACK DEFAULT (1) CHECK (pending = 0 OR pending = 1) 
                    );
                    """
                )
                dbConnection.commit()

                for componentKey in ioSettings.keys():

                    if 'run_interval' in ioSettings[componentKey].keys():

                        if ioSettings[componentKey]['pin_owner'] == True:

                            for pin in ioSettings['pins']:

                                if pin['owner'] == componentKey and pin['active'] == True:

                                    dbCursor.execute(
                                        'INSERT INTO state_event (timestamp, component, type, value, pending) VALUES (?, ?, ?, ?, ?);',
                                        (
                                            timestampEpoch(),
                                            '%(component_key)s_%(gpio)s' % {
                                                'component_key': componentKey,
                                                'gpio': str('00%d' % (pin['gpio'], ))[-2:]
                                            },
                                            'state',
                                            '{"state": "offline"}',
                                            0
                                        )
                                    )

                        else:

                            dbCursor.execute(
                                'INSERT INTO state_event (timestamp, component, type, value, pending) VALUES (?, ?, ?, ?, ?);',
                                (
                                    timestampEpoch(),
                                    componentKey,
                                    'state',
                                    '{"state": "offline"}',
                                    0
                                )
                            )

                dbConnection.commit()

                dbCursor.close()
                dbConnection.close()

                from Database import Database
                from Imager import Imager

                database = Database()
                imager = Imager()

                defaultImage = imager.generateDefault()

                database.metadataMediaAdd(defaultImage)
                database.metadataPlaylistAdd(
                    {
                        'active': True,
                        'name': 'all',
                        'interval': 30.0,
                        'mode': 'shuffle',
                        'sorts': [],
                        'filters': [],
                        'index': 0,
                        'files': [
                            defaultImage['file']
                        ]
                    }
                )

            # Check database
            else:

                dbConnection = sqlite3.connect(
                    paths['database']['path'],
                    check_same_thread=False
                )
                dbCursor = dbConnection.cursor()

                dbCursor.execute(
                    'UPDATE state_event SET value = ?, pending = ? WHERE type = ?;',
                    (
                        '{"state": "offline"}',
                        0,
                        'component'
                    )
                )

                dbCursor.execute(
                    'UPDATE state_event SET pending = ? WHERE type = ?;',
                    (
                        0,
                        'event'
                    )
                )

                dbCursor.close()
                dbConnection.close()

        except Exception as e:

            print('database setup failed')
            return False


        return False

    paths = getPaths()
    ioSettings = jsonLoad(paths['io_settings']['path'])

    databaseSetup = setupDatabase(paths)

    if databaseSetup == False:

        print('could not setup database')
        return


    return True
