import sys

# rpc transports
if sys.platform == 'win32':
    from .win_named_pipe import NamedPipe as StreamingTransport, get_transport_path
elif sys.platform == 'darwin':
    from .unix_domain_socket import get_transport_path, UnixSocket as StreamingTransport
else:
    raise ImportError('Your platform is not supported')
