import pytest
import multiprocessing
import time
import socket
from contextlib import suppress
import os

from bourne_rpc import StreamingTransport, get_transport_path

TEST_UNIX_SOCKET_PATH = r"./test_unix_socket"
TEST_PIPE_NAME = r'\\.\pipe\testpipe'
ECHO_SERVER_BYTES = 10
ECHO_SERVER_ACCEPTED = 2


def echo_server_loop(transport_path):
    """ generates an echo server that returns all received messages with an appropriate
    transport on different platforms"""

    transport = StreamingTransport(transport_path)

    # opening server with transport (echo server)
    transport.bind()
    for responses in range(ECHO_SERVER_ACCEPTED):
        print('pipe open, waiting')
        (connection, name) = transport.accept()

        data = connection.recv(ECHO_SERVER_BYTES)
        print(data)
        connection.sendall(data)


@pytest.fixture
def echo_server():
    transport_path = get_transport_path(application_id='com.crosscloud.unittest')
    return transport_path, multiprocessing.Process(target=echo_server_loop, args=[transport_path])


@pytest.mark.skipif('sys.platform == "win32"')
def test_connect_unix_socket(echo_server):
    """
    Tests a transport (unix sockets) by opening a connection to an echo server, sending
    data and
    checking what comes back
    :param echo_server: a server instance on that transport returning all messages sent
    to it
    """
    # starting server
    echo_server.start()

    for i in range(ECHO_SERVER_ACCEPTED):
        time.sleep(.5)
        # opening and connecting to unix socket
        socket_client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        socket_client.connect(TEST_UNIX_SOCKET_PATH)

        # generating test content to send and get back
        test_content = bytearray(range(ECHO_SERVER_BYTES))

        # sending and receving test data
        socket_client.send(test_content)
        result = socket_client.recv(ECHO_SERVER_BYTES)

        # checking if is equal
        assert test_content == result


@pytest.mark.skipif('sys.platform == "win32"')
def test_unix_socket_file_there():
    """ tests that unix socket is able to handle already existing socket file"""
    with suppress(OSError):
        # deleting unix socket file if exists
        os.unlink(TEST_UNIX_SOCKET_PATH)

    with open(TEST_UNIX_SOCKET_PATH, 'w') as output_file:
        output_file.write('I am wrong content in the unix socket file')

    # creating unix domain socket -> this deletes the path, throws exception if problem
    unix_domain_socket.UnixSocket(path=TEST_UNIX_SOCKET_PATH,
                                  application_id='test_application')


@pytest.mark.skipif('sys.platform == "darwin"')
def test_connect_named_pipes(echo_server):
    """
    Tests a transport (named pipes) by opening a connection to an echo server, sending
    data and
    checking what comes back
    :param echo_server: a server instance on that transport returning all messages sent
    to it
    """

    transport_name, echo_server = echo_server
    # starting server
    echo_server.start()

    for i in range(ECHO_SERVER_ACCEPTED):
        time.sleep(.5)
        # opening named pipe and connecting
        pipe_client = open(transport_name, 'ba+')

        # generating test content to send and get back
        test_content = bytearray(range(ECHO_SERVER_BYTES))

        # sending and receving test data
        pipe_client.write(test_content)
        result = pipe_client.read(ECHO_SERVER_BYTES)

        # checking if is equal
        assert test_content == result


@pytest.mark.skipif('sys.platform == "darwin"')
def test_generate_path_named_pipes(echo_server):
    """tests if the generated path for the transport matches the expected format"""
    application_id = 'test_application_id.test'
    testuser_id = 'testymctestface'
    path = get_transport_path(application_id=application_id,
                              username=testuser_id)

    reference = r'\\.\pipe\test_application_id.test-testymctestface'

    assert path == reference


@pytest.mark.skipif('sys.platform == "win32"')
def test_generate_path_unix_path(echo_server):
    """tests if the generated path for the transport matches the expected format"""
    application_id = 'test_application_id.test'
    path = get_transport_path(application_id=application_id)

    reference = os.path.join(os.path.expanduser('~'), 'Library', 'Group Containers',
                             application_id, 'unix_socket')

    assert path == reference
