

class BourneRpcException(Exception):
    pass

ERROR_PARSE = -32700  # Invalid JSON was received by the server.
# An error occurred on the server while parsing the JSON text.
ERROR_METHOD_NOT_FOUND = -32601  # Method not found	The method does not exist / is not available.
ERROR_INVALID_PARAMS = -32602  # Invalid params	Invalid method parameter(s).
ERROR_INTERNAL = -32603  # Internal error	Internal JSON-RPC error.


class InvalidRequestError(BourneRpcException):
    code = -32600
    message  = 'Invalid Request	The JSON sent is not a valid Request object.'