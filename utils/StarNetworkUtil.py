import hashlib
import threading
import time
from abc import ABCMeta, abstractmethod
from concurrent.futures import ThreadPoolExecutor

from notify import send
from utils.CommonUtil import load_txt, get_thread_number, log, get_proxy_api

lock = threading.RLock()


def encrypt_hash(payload):
    timestamp = int(time.time() * 1000)
    data = (str(payload) + ':D7C92C3FDB52D54147B668DC6F8A5@' + str(timestamp)).replace("'", '"').replace(" ", '')
    sign = hashlib.md5(data.encode()).hexdigest()
    payload['timestamp'] = timestamp
    payload['hash'] = sign
    return payload


def encrypt_key(game, mode, score, timestamp):
    data = '{"game":"' + game + '","mode":"' + mode + '","score":"' + score + '","extra":false}'
    data = data + ':D7C92C3FDB52D54147B668DC6F8A5@' + str(timestamp)
    sign = hashlib.md5(data.encode()).hexdigest()
    return sign


def get_headers(token=None):
    headers = {"User-Agent": "Dart/2.19 (dart:io)"}
    if token is not None and token != '':
        headers['Authorization'] = "Bearer {}".format(token)
    return headers


def is_restrict(text):
    if text.count('Cloudflare to restrict access') > 0 or text.count('You do not have access to') > 0:
        return True
    return False


class StarNetwork(metaclass=ABCMeta):
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


def main(task_name: str, star: StarNetwork, file_name: str = 'StarNetworkGameToken'):
    log.info("=====Star Load Data=====")
    lines = load_txt(file_name)
    log.info("=====End Load Data=====\n")

    log.info("=====Star Load Config=====")
    api_url = get_proxy_api()
    thread_num = get_thread_number(len(lines))
    log.info("=====End Load Config=====\n")

    log.info(f"=====Star {task_name}=====")
    pool = ThreadPoolExecutor(max_workers=thread_num)
    index = 0
    for line in lines:
        index = index + 1
        line = line.strip()
        pool.submit(star.task, index, line, api_url)
    pool.shutdown()
    log.info(f"=====End {task_name}=====\n")

    log.info("=====Star Statistics=====")
    star.statistics()
    log.info("=====End Statistics=====\n")

    log.info("=====Star Save=====")
    star.save()
    log.info("=====End Save=====\n")

    push_data = star.push_data()
    if push_data is not None:
        log.info(f"=====Star Push=====")
        send(task_name, push_data)
        log.info(f"=====End Push=====\n")
