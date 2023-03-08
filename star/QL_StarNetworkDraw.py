"""
cron: 0 30 1/3 * * ?
new Env('StarNetwork抽奖')
"""

import requests

from utils.QLTask import main, QLTask
from utils.CommonUtil import log, get_proxy
from utils.StarNetworkUtil import get_headers, is_exception, encrypt_hash


class StarNetworkDraw(QLTask):
    def task(self, index, text, api_url):
        split = text.split('----')
        email = split[0]
        token = split[len(split) - 1]

        log.info(f"【{index}】{email}----正在抽奖")
        headers = get_headers(token)

        proxy = get_proxy(api_url)

        for i in range(3):
            try:
                resp = requests.get('https://api.starnetwork.io/v3/libra/draw', headers=headers, timeout=15,
                                    proxies={"https": proxy})
                is_exception(resp.text)
                break
            except Exception as ex:
                if repr(ex).count('账号被封禁或登录失效') > 0:
                    log.info(f'【{index}】{email}----账号被封禁或登录失效')
                    return

                if i != 2:
                    log.info(f'【{index}】{email}----进行第{i + 1}次重试----加速抽奖出错：{repr(ex)}')
                    proxy = get_proxy(api_url)
                else:
                    log.info(f'【{index}】{email}----重试完毕----加速抽奖出错：{repr(ex)}')

        for i in range(3):
            try:
                payload = {"id": id, "action": "draw_boost"}
                resp = requests.post('https://api.starnetwork.io/v3/event/draw', json=encrypt_hash(payload), timeout=15,
                                     headers=headers, proxies={"https": proxy})
                if is_exception(resp.text):
                    raise Exception('访问被拒绝')
                break
            except Exception as ex:
                if repr(ex).count('账号被封禁或登录失效') > 0:
                    log.info(f'【{index}】{email}----账号被封禁或登录失效')
                    return

                if i != 2:
                    log.info(f'【{index}】{email}----进行第{i + 1}次重试----令牌抽奖出错：{repr(ex)}')
                    proxy = get_proxy(api_url)
                else:
                    log.info(f'【{index}】{email}----重试完毕----令牌抽奖出错：{repr(ex)}')

    def statistics(self):
        pass

    def save(self):
        pass

    def push_data(self):
        return None


if __name__ == '__main__':
    main("StarNetwork抽奖", StarNetworkDraw(), 'StarNetworkToken')
