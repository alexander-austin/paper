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
        'metadata': {
            'type': 'json',
            'publish': False,
            'path': os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.realpath(__file__)
                    )
                ),
                'data',
                'metadata.json'
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
