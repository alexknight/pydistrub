# coding=utf-8
import logging
import os
import sys
import traceback
from concurrent import futures

import grpc

from Common import logging_config
from configs.Strategy import Addr
from protos import pydistrub_pb2, pydistrub_pb2_grpc


class TaskHandler(object):
    pass


class TaskWorker(pydistrub_pb2_grpc.InvokeRemote):

    def __init__(self, task_handler):
        self.task_handler = task_handler

    def TaskDispatcher(self, request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False,
                       compression=None, wait_for_ready=None, timeout=None, metadata=None):
        response_data = None
        try:
            logging.info('msg_type: {} params: {}'.format(request.remote_func, request.params))
            func = getattr(self.task_handler, request.remote_func)
            ret = func(request.params) if request.params else func()
            response_data = {'ret_code': 200, 'ret_msg': ''}
        except Exception as e:
            response_data = {'ret_code': 4001, 'ret_msg': ''.join(traceback.format_exception(*sys.exc_info()))}
            raise Exception(''.join(traceback.format_exception(*sys.exc_info())))
        finally:
            response = pydistrub_pb2.RetObject(
                msg_type=request.remote_func,
                response_data=response_data)
            return response

    def Close(self, request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False,
              compression=None, wait_for_ready=None, timeout=None, metadata=None):

        response = pydistrub_pb2.RetObject()
        return response


def run_forever(master):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))

    pydistrub_pb2_grpc.add_InvokeRemoteServicer_to_server(master, server)

    server.add_insecure_port(Addr.MasterServerAddress)
    logging_config(os.getcwd())
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    master = TaskWorker(TaskHandler())
    run_forever(master)
