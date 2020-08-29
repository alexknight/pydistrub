# coding=utf-8
import logging
import os
import sys
import threading
import traceback
from concurrent import futures

import grpc

from Common import logging_config
from RequestClient import ReqClient
from configs.Strategy import Addr
from protos import pydistrub_pb2, pydistrub_pb2_grpc

SERVER_ADDRESS = 'localhost:10021'


class DispatchMater(pydistrub_pb2_grpc.InvokeRemote):

    def __init__(self):
        self.workers_handler = []
        self.task_index = 0
        self.event = threading.Event()

    def register_worker_handler(self, worker_handler: ReqClient):
        if worker_handler not in self.workers_handler:
            self.workers_handler.append(worker_handler)

    def TaskApply(self, request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False,
                  compression=None, wait_for_ready=None, timeout=None, metadata=None):
        if not self.workers_handler:
            return pydistrub_pb2.ApplyResponse(ret_obj=pydistrub_pb2.RetObject(ret_code=401,
                                                                               ret_msg='No avalible worker.'))
        client_id = request.client_id
        return pydistrub_pb2.ApplyResponse(ret_obj=pydistrub_pb2.RetObject(ret_code=200))

    def TaskDispatcher(self, request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False,
                       compression=None, wait_for_ready=None, timeout=None, metadata=None):
        response_data = None
        remote_func = request.remote_func
        worker_handler = self.workers_handler[self.task_index]
        if self.task_index == len(self.workers_handler) - 1:
            self.task_index = 0
        else:
            self.task_index += 1
        try:
            logging.info('msg_type: {} params: {}'.format(remote_func, request.params))
            ret = worker_handler.invoke_remote(remote_func=remote_func, params=request.params)
            logging.info('msg_type: {} ret: {}'.format(remote_func, ret))
            response_data = {'ret_code': 200, 'ret_msg': ''}
        except Exception as e:
            response_data = {'ret_code': 4001, 'ret_msg': ''.join(traceback.format_exception(*sys.exc_info()))}
            raise Exception(''.join(traceback.format_exception(*sys.exc_info())))
        finally:
            response = pydistrub_pb2.RetObject(
                msg_type=remote_func,
                response_data=response_data)
            return response

    def Close(self, request, target, options=(), channel_credentials=None, call_credentials=None, insecure=False,
              compression=None, wait_for_ready=None, timeout=None, metadata=None):
        self.event.set()

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
    master = DispatchMater()
    for worker_addr in Addr.WorkerAddress:
        master.register_worker_handler(ReqClient(Addr.WorkerAddress))
    run_forever(master)
