#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import functools
import inspect
import logging


def step_info(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        called_func = inspect.stack()[1][1].split('/')[-1].split('\\')[-1] + '(line:{}).'.format(
          str(inspect.stack()[1][2])) + inspect.stack()[1][4][0].strip()
        logging.info('\n---> on {}, waiting task finish...\n'.format(called_func))
        res = func(*args, **kwargs)
        logging.info('\n<--- on {}, task finish...\n'.format(called_func))
        return res
    return _wrapper


def logging_config(log_dir):
    """
    日志配置, 可以参考http://www.cnblogs.com/dkblog/archive/2011/08/26/2155018.html
    :param log_dir: 存放日志的目录
    :return:
    """
    # 配置输出到文件
    dst_log_dir = log_dir + '/ui_auto.log'
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s-%(filename)s-%(funcName)s[pid:%(process)d][tid:%(thread)d][line:%(lineno)d]-%(levelname)s: %(message)s',
                        filename=dst_log_dir)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)

    # 配置输出到控制台
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s-%(filename)s-%(funcName)s[pid:%(process)d][tid:%(thread)d][line:%(lineno)d]-%(levelname)s: %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


