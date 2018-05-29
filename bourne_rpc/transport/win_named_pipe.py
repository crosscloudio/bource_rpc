import ctypes
import ctypes.wintypes
import logging
import contextlib
import os

logger = logging.getLogger(__name__)

INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value


def _errcheck_bool(value, _, args):
    if not value:
        raise ctypes.WinError()
    return args


def _errcheck_handle(value, _, args):
    if not value:
        raise ctypes.WinError()
    if value == INVALID_HANDLE_VALUE:
        raise ctypes.WinError()
    return args


def _errcheck_dword(value, _, args):
    if value == 0xFFFFFFFF:
        raise ctypes.WinError()
    return args


def _errcheck_fail_zero(value, _, args):
    """ checks if the value is zero and fails then"""
    if value == 0:
        raise ctypes.WinError()
    return args


class OVERLAPPED(ctypes.Structure):
    _fields_ = [('Internal', ctypes.wintypes.LPVOID),
                ('InternalHigh', ctypes.wintypes.LPVOID),
                ('Offset', ctypes.wintypes.DWORD),
                ('OffsetHigh', ctypes.wintypes.DWORD),
                ('Pointer', ctypes.wintypes.LPVOID),
                ('hEvent', ctypes.wintypes.HANDLE)]


LPOVERLAPPED = ctypes.POINTER(OVERLAPPED)


class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [('nLength', ctypes.wintypes.LPVOID),
                ('lpSecurityDescriptor', ctypes.wintypes.LPVOID),
                ('bInheritHandle', ctypes.wintypes.DWORD)]


LPSECURITY_ATTRIBUTES = ctypes.POINTER(SECURITY_ATTRIBUTES)

CreateEvent = ctypes.windll.kernel32.CreateEventW
CreateEvent.restype = ctypes.wintypes.HANDLE
CreateEvent.errcheck = _errcheck_handle
CreateEvent.argtypes = (
    ctypes.wintypes.LPVOID,  # lpEventAttributes
    ctypes.wintypes.BOOL,  # bManualReset
    ctypes.wintypes.BOOL,  # bInitialState
    ctypes.wintypes.LPCWSTR,  # lpName
)

CreateNamedPipe = ctypes.windll.kernel32.CreateNamedPipeW
CreateNamedPipe.restype = ctypes.wintypes.HANDLE
CreateNamedPipe.errcheck = _errcheck_handle
CreateNamedPipe.argtypes = (
    ctypes.wintypes.LPCWSTR,  # lpName,
    ctypes.wintypes.DWORD,  # dwOpenMode,
    ctypes.wintypes.DWORD,  # dwPipeMode,
    ctypes.wintypes.DWORD,  # nMaxInstances,
    ctypes.wintypes.DWORD,  # nOutBufferSize,
    ctypes.wintypes.DWORD,  # nInBufferSize,
    ctypes.wintypes.DWORD,  # nDefaultTimeOut,
    LPSECURITY_ATTRIBUTES  # lpSecurityAttributes
)

ConnectNamedPipe = ctypes.windll.kernel32.ConnectNamedPipe
ConnectNamedPipe.restype = ctypes.wintypes.HANDLE
ConnectNamedPipe.errcheck = _errcheck_bool
ConnectNamedPipe.argtypes = (
    ctypes.wintypes.HANDLE,  # hNamedPipe,
    LPOVERLAPPED  # lpOverlapped
)

PIPE_ACCESS_DUPLEX = 0x00000003
PIPE_TYPE_BYTE = 0x00000000
PIPE_READMODE_BYTE = 0x00000000
PIPE_WAIT = 0x00000000
PIPE_REJECT_REMOTE_CLIENTS = 0x00000008
PIPE_UNLIMITED_INSTANCES = 255

ReadFile = ctypes.windll.kernel32.ReadFile
ReadFile.restype = ctypes.wintypes.BOOL
ReadFile.errcheck = _errcheck_bool
ReadFile.argtypes = (
    ctypes.wintypes.HANDLE,  # hFile
    ctypes.wintypes.LPVOID,  # lpBuffer
    ctypes.wintypes.DWORD,  # nNumberOfBytesToRead
    ctypes.wintypes.LPDWORD,  # lpNumberOfBytesRead
    LPOVERLAPPED,  # lpOverlapped
)

WriteFile = ctypes.windll.kernel32.WriteFile
WriteFile.restype = ctypes.wintypes.BOOL
WriteFile.errcheck = _errcheck_bool
WriteFile.argtypes = (
    ctypes.wintypes.HANDLE,  # hFile,
    ctypes.wintypes.LPCVOID,  # lpBuffer,
    ctypes.wintypes.DWORD,  # nNumberOfBytesToWrite,
    ctypes.wintypes.LPDWORD,  # lpNumberOfBytesWritten,
    LPOVERLAPPED  # lpOverlapped
)

CloseHandle = ctypes.windll.kernel32.CloseHandle
CloseHandle.restype = ctypes.wintypes.BOOL
CloseHandle.argtypes = (ctypes.wintypes.HANDLE,)
CloseHandle.errcheck = _errcheck_bool

DisconnectNamedPipe = ctypes.windll.kernel32.DisconnectNamedPipe
DisconnectNamedPipe.restype = ctypes.wintypes.BOOL
DisconnectNamedPipe.argtypes = (ctypes.wintypes.HANDLE,)
DisconnectNamedPipe.errcheck = _errcheck_bool

FlushFileBuffers = ctypes.windll.kernel32.FlushFileBuffers
FlushFileBuffers.restype = ctypes.wintypes.BOOL
FlushFileBuffers.argtypes = (ctypes.wintypes.HANDLE,)
FlushFileBuffers.errcheck = _errcheck_bool

CancelIoEx = ctypes.windll.kernel32.CancelIoEx
CancelIoEx.restype = ctypes.wintypes.BOOL
CancelIoEx.argtypes = (ctypes.wintypes.HANDLE, LPOVERLAPPED)
CancelIoEx.errcheck = _errcheck_bool


class NamedPipe:
    def __init__(self, path, handle=None):
        self.pipe_name = path

        self.handle = handle

    def bind(self):
        """ does nothing and is just for interop with sockets """

    def accept(self, max_connections=16, recv_buffer_size=255, send_buffer_size=255, timeout=50):
        """ :returns a NamedPipe object with the new connection """
        self.handle = CreateNamedPipe(self.pipe_name,
                                      PIPE_ACCESS_DUPLEX,
                                      PIPE_TYPE_BYTE | PIPE_READMODE_BYTE | PIPE_WAIT | PIPE_REJECT_REMOTE_CLIENTS,
                                      max_connections,
                                      send_buffer_size,  # buffer size
                                      recv_buffer_size,  # in buffer size
                                      timeout,  # timeout
                                      None
                                      )

        logger.debug("waiting for a new connection")
        ConnectNamedPipe(self.handle, None)
        result = NamedPipe(self.pipe_name, self.handle), self.pipe_name
        self.handle = None
        return result

    def sendall(self, b):
        bytes_written = ctypes.wintypes.DWORD()
        WriteFile(self.handle, b, len(b), ctypes.byref(bytes_written), None)
        FlushFileBuffers(self.handle)

    def recv(self, bufsize):
        buffer = ctypes.create_string_buffer(bufsize)

        bytes_read = ctypes.wintypes.DWORD()
        ReadFile(self.handle,
                 ctypes.byref(buffer),
                 bufsize,
                 ctypes.byref(bytes_read),
                 None)
        return buffer.raw[:bytes_read.value]

    def close(self):
        logger.debug("cancelling io")
        with contextlib.suppress(WindowsError):
            CancelIoEx(self.handle, None)

        logger.debug("disconnect pipe")
        with contextlib.suppress(WindowsError):
            DisconnectNamedPipe(self.handle)

        logger.debug("closing pipe")
        with contextlib.suppress(WindowsError):
            CloseHandle(self.handle)

        logger.debug("closed")

    def __del__(self):
        self.close()


def get_transport_path(application_id, username=os.getlogin()):
    """
    returns a unique path for the transport to operate on dependent on os,
    username and application id.

    :param username: the username of the currently logged in user
    :param application_id: the identifier of the application.
    This needs to be unique for different transports (applications) running.
    :return: a platform specific path to a transport unique for the user and
    application
    """
    return r'\\.\pipe\{}-{}'.format(application_id, username)
