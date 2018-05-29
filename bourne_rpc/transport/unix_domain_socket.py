import socket
import os
from contextlib import suppress


class UnixSocket:
    """ Implementation of a transport layer using unix domain sockets. Please refer to
    https://en.wikipedia.org/wiki/Unix_domain_socket for more information """

    def __init__(self, path):
        """
        initializes a new unix socket transport
        :param path: the path to the file the unix socket shall be opened under
        """

        self.socket_path = path

        # creating directories of path
        with suppress(FileExistsError):
            os.makedirs(os.path.dirname(self.socket_path))

        with suppress(FileNotFoundError):
            # deleting unix socket file if exists
            os.unlink(self.socket_path)

        # creating unix socket
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    def bind(self):
        """ binds the socket to a configured address (=file as we are using
        unix domain sockets) """
        # binding socket to configured address
        self.socket.bind(self.socket_path)

        # opening up pipes for messages - not defining size of queue here as default
        # value is chosen 'appropriately' by default - hard to find out what that means
        # though...
        self.socket.listen(socket.SOMAXCONN)

    def accept(self):
        """ accepts a connection from the socket"""
        return self.socket.accept()

    def sendall(self, b):
        """
        ends data to the socket
        :param b: the data to be sent
        """
        self.socket.sendall(data=b)

    def recv(self, bufsize):
        """
        Receives data from the socket
        :param bufsize:
        :return: the read data
        """
        return self.socket.recv(buffersize=bufsize)

    def close(self):
        """closes the socket"""
        self.socket.close()

    def __del__(self):
        """destructor like"""
        self.close()


def get_transport_path(application_id):
    """
    returns a unique path for the transport to operate on dependent on os,
    username and application id. Note macOS: this library generates a transport
    under the app group container for a specific shell extension under
    ~/Library/GroupContainers/[application_id]/. This way, a sandboxed shell
    extension will be able to reach the transport given proper configuration for
    group containers (https://developer.apple.com/library/content/documentation
    /IDEs/Conceptual/AppDistributionGuide/AddingCapabilities/AddingCapabilities
    .html).
    :param application_id: the identifier of the application. This needs to be unique
    for different transports (applications) running. On MacOS,
    the application_id passed must match the bundle identifier of the
    shell extension app (e.g. FinderSync App).
    :return: a platform specific path to a transport unique for the user and
    application
    """
    return os.path.join(os.path.expanduser('~'), 'Library', 'Group Containers',
                        application_id, 'unix_socket')
