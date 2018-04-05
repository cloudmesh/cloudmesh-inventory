
host = {
    'schema': {
        'name': {
            'type': 'string'
        },
        'cluster': {
            'type': 'string'
        },
        'label': {
            'type': 'string'
        },
        'service': {
            'type': 'string'
        },
        'os': {
            'type': 'string'
        },
        'ip': {
            'type': 'dict',
            'schema': {
                'public': {
                    'type': 'string'
                },
                'private': {
                    'type': 'string'
                }
            }
        },
        'project': {
            'type': 'string'
        },
        'owners': {
            'type': 'list',
            'schema': {
                'type': 'string'
            }
        },
        'comment': {
            'type': 'string'
        },
        'description': {
            'type': 'string'
        },
        'metadata': {
            'type': 'string'
        }
    }
}

# noinspection SpellCheckingInspection
eve_settings = {
    'MONGO_HOST': 'localhost',
    'MONGO_DBNAME': 'testing',
    'RESOURCE_METHODS': ['GET', 'POST', 'DELETE'],
    'BANDWIDTH_SAVER': False,
    'DOMAIN': {
        'host': host,
    },
}
