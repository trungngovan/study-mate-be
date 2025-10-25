"""
OpenAPI schema documentation for matching app endpoints.
"""

SEND_CONNECTION_REQUEST_SCHEMA = {
    'summary': 'Send connection request',
    'description': 'Send a connection request to another user',
    'tags': ['Matching - Requests'],
}

GET_CONNECTION_REQUEST_SCHEMA = {
    'summary': 'Get connection request',
    'description': 'Get details of a specific connection request',
    'tags': ['Matching - Requests'],
}

LIST_CONNECTION_REQUESTS_SCHEMA = {
    'summary': 'List connection requests',
    'description': 'List all connection requests (sent and received)',
    'tags': ['Matching - Requests'],
}

ACCEPT_CONNECTION_REQUEST_SCHEMA = {
    'summary': 'Accept connection request',
    'description': 'Accept a pending connection request and create a connection.',
    'tags': ['Matching - Requests'],
}

REJECT_CONNECTION_REQUEST_SCHEMA = {
    'summary': 'Reject connection request',
    'description': 'Reject a pending connection request',
    'tags': ['Matching - Requests'],
}

BLOCK_CONNECTION_SCHEMA = {
    'summary': 'Block connection',
    'description': 'Block a connection request or existing connection',
    'tags': ['Matching - Requests'],
}

LIST_SENT_REQUESTS_SCHEMA = {
    'summary': 'List sent requests',
    'description': 'List connection requests sent by the current user',
    'tags': ['Matching - Requests'],
}

LIST_RECEIVED_REQUESTS_SCHEMA = {
    'summary': 'List received requests',
    'description': 'List connection requests received by the current user',
    'tags': ['Matching - Requests'],
}

LIST_PENDING_REQUESTS_SCHEMA = {
    'summary': 'List pending requests',
    'description': 'List all pending connection requests (both sent and received)',
    'tags': ['Matching - Requests'],
}

LIST_CONNECTIONS_SCHEMA = {
    'summary': 'List connections',
    'description': 'List all accepted connections for the current user',
    'tags': ['Matching - Connections'],
}

GET_CONNECTION_SCHEMA = {
    'summary': 'Get connection details',
    'description': 'Get details of a specific accepted connection',
    'tags': ['Matching - Connections'],
}

CONNECTION_STATISTICS_SCHEMA = {
    'summary': 'Connection statistics',
    'description': 'Get connection statistics for the current user including pending requests and accepted connections',
    'tags': ['Matching - Connections'],
}

CONNECTION_STATUS_SCHEMA = {
    'summary': 'Check connection status',
    'description': 'Check the connection status between current user and another user',
    'tags': ['Matching - Connections'],
}
