"""
cron: 0 0 0 * * ?
new Env('StarNetwork练习游戏')
"""
import random
import time

import requests

from ql_task import main, QLTask
from utils.CommonUtil import log, lock, get_proxy
from utils.StarNetworkUtil import encrypt_key, get_headers, is_exception


class StarNetworkPracticeGame(QLTask):
    def __init__(self):
        self.total_count = 0
        self.success_count = 0
        self.fail_email = []
        self.games = ['ballz', 'block_puzzle', 'brain_workout', 'puzzle_2048', 'sudoku', 'flappy']

    def task(self, index, text, api_url):
        split = text.split('----')
        email = split[0]
        token = split[len(split) - 1]

        lock.acquire()
        self.total_count += 1
        lock.release()

        log.info(f"【{index}】{email}----正在完成练习")
        delay = random.randint(1, 300)
        log.info(f"【{index}】{email}----随机延迟{delay}秒后开始")
        time.sleep(delay)
        headers = get_headers(token)
        proxy = get_proxy(api_url)
        for game in self.games:
            if game == 'flappy':
                score = str(random.randint(100, 200))
            elif game == 'puzzle_2048':
                score = str(random.randint(12345, 23333))
            else:
                score = str(random.randint(8888, 10000))

            for i in range(3):
                try:
                    timestamp = int(time.time() * 1000)
                    payload = {"game": game, "mode": "practice", "score": score, "extra": False, "timestamp": timestamp,
                               "key": encrypt_key(game, "practice", score, timestamp)}
                    resp = requests.post("https://api.starnetwork.io/v3/game/record", json=payload, headers=headers,
                                         proxies={"https": proxy}, timeout=15)
                    if resp.text.count('id') > 0 and resp.text.count('SAVED') > 0:
                        if resp.text.count('reward') > 0:
                            log.info(f'【{index}】{email}----【{game}】练习成功：获得奖励')
                        elif resp.text.count('id') > 0 and resp.text.count('SAVED') > 0:
                            log.info(f'【{index}】{email}----【{game}】练习成功：未获得奖励')
                        lock.acquire()
                        self.success_count += 1
                        lock.release()
                        break
                    is_exception(resp.text)
                    raise Exception(resp.text)
                except Exception as ex:
                    if repr(ex).count('账号被封禁或登录失效') > 0:
                        log.info(f'【{index}】{email}----账号被封禁或登录失效')
                        return

                    if i != 2:
                        log.info(f'【{index}】{email}----进行第{i + 1}次重试----【{game}】完成练习出错：{repr(ex)}')
                        proxy = get_proxy(api_url)
                    else:
                        log.info(f'【{index}】{email}----重试完毕----【{game}】完成练习出错：{repr(ex)}')
                        self.fail_email.append(f'【{index}】{email}----【{game}】完成练习出错：{repr(ex)}')

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
    main('StarNetwork练习游戏', StarNetworkPracticeGame(), 'StarNetworkToken')
