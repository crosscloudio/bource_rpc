import pytest

from bourne_rpc import server, exceptions


@pytest.mark.parametrize("req", [
    {},
    {'jsonrpc': '123'},
    {'jsonrpc': '2.0'},
    {'jsonrpc': '2.0', 'method': 'hello'},
    {'jsonrpc': '2.0', 'id': 123},
    {'method': 'hello'},
    {'method': 'hello', 'id': 123},
    {'id': 123},
])
def test_validation(req):
    with pytest.raises(exceptions.InvalidRequestError):
        server.validate_request(req)
