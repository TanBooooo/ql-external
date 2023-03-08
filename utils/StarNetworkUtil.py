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


def is_exception(text):
    if text.count('Cloudflare to restrict access') > 0 or text.count('You do not have access to') > 0:
        raise Exception('访问被拒绝')
    if text.count('You are not authr') > 0:
        raise Exception('账号被封禁或登录失效')
