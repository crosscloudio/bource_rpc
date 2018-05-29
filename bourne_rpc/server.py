import contextlib
import json
import struct
import threading
import logging
import os

from . import exceptions

logger = logging.getLogger(__name__)


def validate_request(request):
    """ Checks if a request fullfills the JSON-RPC 2.0 specs.
    :param request a dict
    :raise InvalidRequestError"""

    if not request.get('jsonrpc') == '2.0':
        raise exceptions.InvalidRequestError('jsonrpc field is missing or not set to 2.0')

    for field in ['id', 'method']:
        if field not in request:
            raise exceptions.InvalidRequestError(
                '{} is missing in request object'.format(field))


class RpcServer:
    def __init__(self, transport, obj):
        self.transport = transport
        self.obj = obj

    def serve(self):
        while 1:
            try:
                transport, addr = self.transport.accept()
                logger.info('Got new client from "%s"', addr)
                threading.Thread(target=self.handler, args=(transport,)).start()
            except WindowsError as ex:
                if ex.winerror == 995:
                    logger.debug("io got canceled, that means this is a shutdown request")
                    break
                else:
                    raise

    def stop(self):
        self.transport.close()

    def handler(self, com_socket):
        with contextlib.closing(com_socket):
            while 1:
                try:
                    msg_length, = struct.unpack('I', com_socket.recv(4))
                except BrokenPipeError:
                    com_socket.close()
                    logger.debug('connection closed')
                    return
                message = com_socket.recv(msg_length).decode('utf8')
                logger.debug('--> %s', message)

                request_msg = json.loads(message)

                response = {'jsonrpc': '2.0', 'id': request_msg['id']}
                try:
                    validate_request(request_msg)
                    params = request_msg.get('params', [])
                    logger.debug(params)

                    return_value = getattr(self.obj, request_msg['method'])(*params)
                    response['result'] = return_value
                except exceptions.InvalidRequestError as e:
                    logger.exception("Failed to handle request")
                    response['error'] = {'code': e.code, 'message': e.message}
                except:
                    logger.exception("Failed to handle request")
                    response['error'] = {'code': exceptions.ERROR_INTERNAL,
                                         'message': 'Unknown error.'}
                finally:
                    # send response
                    response_message = json.dumps(response).encode('utf-8')
                    logger.debug('<-- %s', response_message)
                    com_socket.sendall(struct.pack('I', len(response_message)))
                    com_socket.sendall(response_message)
