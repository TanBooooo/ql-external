import logging
import os
import re
import sys
import threading
import time
from abc import ABCMeta, abstractmethod
from concurrent.futures import ThreadPoolExecutor

import requests

from notify import send

logging.basicConfig(
    level=logging.INFO,
    datefmt="%H:%M:%S",
    format='%(asctime)s [%(lineno)d] %(levelname)s %(message)s',
)
log = logging.getLogger()


def load_txt(file_name):
    """读取文本"""
    file_name = file_name + ".txt"
    count = 0
    lines = []
    while os.path.exists(file_name) is False:
        log.error(f"不存在{file_name}文件，3秒后重试")
        time.sleep(3)

    log.info(f"正在读取{file_name}文本信息")
    with open(sys.path[0] + "/" + file_name, "r+") as f:
        while True:
            line = f.readline().strip()
            if line is None or line == '':
                break
            count = count + 1
            lines.append(line)
    log.info("TXT读取完毕，总计数量: {}".format(count))
    return lines


def write_txt(file_name, text, append=False):
    """读取文本"""
    mode = 'w+'
    if append:
        mode = 'a+'
    with open(sys.path[0] + "/" + file_name + ".txt", mode) as f:
        f.write(text)


def del_txt(file_name):
    """删除文本"""
    file_name = file_name + ".txt"
    if os.path.isfile(file_name):
        try:
            os.remove(file_name)  # 这个可以删除单个文件，不能删除文件夹
        except BaseException as e:
            log.error(f"文件删除失败:{repr(e)}")
    else:
        log.error(f"{file_name}不存在或不是一个文件")


def get_thread_number(size, thread_name: str = 'ThreadNum'):
    """获取线程数"""
    thread_num = 5
    value = get_env(thread_name)
    if value is not None:
        try:
            thread_num = int(value)
        except Exception:
            log.info(f"线程数设置有误，设置默认数量{thread_num}")
    else:
        log.info(f"暂未设置线程数，默认数量{thread_num}")

    if thread_num > size:
        thread_num = size
        log.info(f"线程数量大于文本数量，设置文本数量{size}")

    if thread_num < 1:
        thread_num = 1
        log.info("线程数量不能小于0，设置默认数量1")

    return thread_num


def get_proxy_api(application: str = None, proxy_name: str = 'Proxy_API'):
    """获取代理API"""
    api_url = ''
    if application is not None and application != '':
        items = get_env('Disable_Proxy').split('&')
        if application in items:
            log.info("当前任务已禁用代理")
            return api_url

    api_url = get_env(proxy_name)
    if api_url is None or api_url == '':
        log.info("暂未设置代理API，默认不代理")
    return api_url


def get_env(env_name):
    """获取环境变量"""
    try:
        if env_name in os.environ:
            env_val = os.environ[env_name]
            if len(env_val) > 0:
                log.info(f"获取到环境变量【{env_name}】")
                return env_val
        log.info(f"暂未设置环境变量【{env_name}】")
    except Exception as e:
        log.error(f"环境变量【{env_name}】获取出错: {repr(e)}")
    return None


proxies = []
lock = threading.RLock()


def get_proxy(api_url):
    """提取代理"""
    if api_url is None or api_url == '':
        return None

    lock.acquire()
    if len(proxies) > 0:
        for i in range(3):
            try:
                res = requests.get(api_url)
                ips = re.findall('(?:\d+\.){3}\d+:\d+', res.text)
                if len(ips) < 1:
                    log.error(f"API代理提取响应:{res.text}")
                    raise Exception('代理提取失败')
                else:
                    for ip in ips:
                        proxies.append(f'http://{ip}')
                    break
            except Exception:
                if i != 2:
                    log.error(f"API代理提取出错，请检查余额或是否已添加白名单,1S后第{i + 1}次重试")
                    time.sleep(1)
                else:
                    log.error("API代理提取出错，请检查余额或是否已添加白名单,重试完毕")

    if len(proxies) > 0:
        proxy = proxies.pop(0)
        log.info("当前代理:{}".format(proxy))
    else:
        proxy = None
    lock.release()
    return proxy


class QLTask(metaclass=ABCMeta):
    @abstractmethod
    def task(self, index, text, api_url):
        """主任务"""
        pass

    @abstractmethod
    def statistics(self):
        """统计"""
        pass

    @abstractmethod
    def save(self):
        """保存数据"""
        pass

    @abstractmethod
    def push_data(self):
        """获取推送数据"""
        pass


def main(task_name: str, ql: QLTask, file_name: str):
    log.info("=====Start Load Data=====")
    lines = load_txt(file_name)
    log.info("=====End Load Data=====\n")

    log.info("=====Start Load Config=====")
    api_url = get_proxy_api()
    thread_num = get_thread_number(len(lines))
    log.info("=====End Load Config=====\n")

    log.info(f"=====Start {task_name}=====")
    pool = ThreadPoolExecutor(max_workers=thread_num)
    index = 0
    for line in lines:
        index = index + 1
        line = line.strip()
        pool.submit(ql.task, index, line, api_url)
    pool.shutdown()
    log.info(f"=====End {task_name}=====\n")

    log.info("=====Start Statistics=====")
    ql.statistics()
    log.info("=====End Statistics=====\n")

    log.info("=====Start Save=====")
    ql.save()
    log.info("=====End Save=====\n")

    push_data = ql.push_data()
    if push_data is not None:
        log.info(f"=====Start Push=====")
        send(task_name, push_data)
        log.info(f"=====End Push=====\n")
