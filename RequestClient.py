# coding=utf-8
import logging
import os

import grpc

from Common import logging_config
from configs.Strategy import Addr
from protos import pydistrub_pb2, pydistrub_pb2_grpc

SERVER_ADDRESS = "localhost:10021"


class ReqClient(object):
    def __init__(self, address):
        self.channel = grpc.insecure_channel(address)
        self.stub = pydistrub_pb2_grpc.InvokeRemoteStub(self.channel)

    def invoke_remote(self, remote_func, params, option):
        if params is None:
            params = {}
        request = pydistrub_pb2.Request(remote_func=remote_func, params=params, option=option)
        response = self.stub.TaskDispatcher(request)
        if response.response_data.ret_code != 200:
            except_msg = response.response_data.ret_msg
            for line in except_msg.splitlines():
                logging.error(line)
            raise Exception(except_msg)
        else:
            logging.info("resp from server({}), the message={}".format(response.msg_type, response.response_data))

    def on_finish(self):
        logging.info("self.channel: {}".format(id(self.channel)))
        request = pydistrub_pb2.Void()
        self.stub.Close(request)
        self.channel.close()


def run_client(connect_to):
    logging_config(os.getcwd())
    req_client = ReqClient(connect_to)
    req_client.invoke_remote(remote_func='on_create', params={}, option={'allocate_to': ['192.168.1.1', '192.168.1.2']})
    req_client.on_finish()


if __name__ == '__main__':
    run_client(connect_to=Addr.MasterServerAddress)
