"""
cron: 50 59 1 * * ?
new Env('StarNetwork游戏-Puzzle2048')
"""
import datetime
import random
import time

import requests

from utils.QLTask import main, QLTask
from utils.CommonUtil import log, lock, get_proxy
from utils.StarNetworkUtil import get_headers, encrypt_key, is_exception


class StarNetworkGame(QLTask):
    def __init__(self, game):
        self.game = game
        self.total_count = 0
        self.success_count = 0
        self.fail_email = []

    def task(self, index, text, api_url):
        split = text.split('----')
        email = split[0]
        if split[len(split) - 2] != self.game:
            return
        token = split[len(split) - 1]
        lock.acquire()
        self.total_count += 1
        lock.release()

        log.info(f"【{index}】{email}----正在完成游戏")
        headers = get_headers(token)
        proxy = get_proxy(api_url)

        if 'flappy' == self.game:
            score = "200"
            while True:
                second = float(datetime.datetime.now().strftime('%S.%f'))
                if second > 55 or second < 10:
                    try:
                        timestamp = int(time.time() * 1000)
                        payload = {"game": self.game, "mode": "tournament", "score": score, "extra": False,
                                   "timestamp": timestamp,
                                   "key": encrypt_key(self.game, 'tournament', score, timestamp)}
                        resp = requests.post("https://api.starnetwork.io/v3/game/record", json=payload, headers=headers,
                                             proxies={"https": proxy}, timeout=15)
                        is_exception(resp.text)

                        if resp.text.count('id') > 0 and resp.text.count('SAVED') > 0:
                            log.info(f'【{index}】{email}----完成游戏成功')
                        else:
                            raise Exception(resp.text)
                    except Exception as ex:
                        if repr(ex).count('账号被封禁或登录失效') > 0:
                            log.info(f'【{index}】{email}----账号被封禁或登录失效')
                            return
                        log.error(f'【{index}】{email}----完成游戏出错：{ex}')
                else:
                    return

        for i in range(3):
            try:
                score = str(random.randint(9888, 10000))
                timestamp = int(time.time() * 1000)
                payload = {"game": self.game, "mode": "tournament", "score": score, "extra": False,
                           "timestamp": timestamp, "key": encrypt_key(self.game, 'tournament', score, timestamp)}
                resp = requests.post("https://api.starnetwork.io/v3/game/record", json=payload, headers=headers,
                                     timeout=15, proxies={"https": proxy})
                is_exception(resp.text)

                if resp.text.count('id') > 0 and resp.text.count('SAVED') > 0:
                    break
            except Exception as ex:
                if repr(ex).count('账号被封禁或登录失效') > 0:
                    log.info(f'【{index}】{email}----账号被封禁或登录失效')
                    return

        for i in range(3):
            try:
                score = '899999'
                timestamp = int(time.time() * 1000)
                payload = {"game": self.game, "mode": "tournament", "score": score, "extra": False,
                           "timestamp": timestamp, "key": encrypt_key(self.game, 'tournament', score, timestamp)}
                resp = requests.post("https://api.starnetwork.io/v2/game/record", json=payload, headers=headers,
                                     timeout=15, proxies={"https": proxy})
                is_exception(resp.text)

                if resp.text.count('id') > 0 and resp.text.count('SAVED') > 0:
                    log.info(f'【{index}】{email}----完成游戏成功')
                    lock.acquire()
                    self.success_count += 1
                    lock.release()
                    break
                else:
                    raise Exception(resp.text)
            except Exception as ex:
                if repr(ex).count('账号被封禁或登录失效') > 0:
                    log.info(f'【{index}】{email}----账号被封禁或登录失效')
                    return

                if i != 2:
                    log.info(f'【{index}】{email}----进行第{i + 1}次重试----完成游戏出错：{repr(ex)}')
                    proxy = get_proxy(api_url)
                else:
                    log.info(f'【{index}】{email}----重试完毕----完成游戏出错：{repr(ex)}')
                    self.fail_email.append(f'【{index}】{email}----完成游戏出错：{repr(ex)}')

    def statistics(self):
        if len(self.fail_email) > 0:
            log.info(f"-----Fail Statistics-----")
            log_data = ''
            for fail in self.fail_email:
                log_data += fail + '\n'
            log.error(f'\n{log_data}')

    def save(self):
        pass

    def push_data(self):
        return f'总任务数：{self.total_count}\n任务成功数：{self.success_count}\n任务失败数：{len(self.fail_email)}'


if __name__ == '__main__':
    main('StarNetwork游戏-Puzzle2048', StarNetworkGame("puzzle_2048"), 'StarNetworkGameToken')
