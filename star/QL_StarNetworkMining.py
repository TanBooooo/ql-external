"""
cron: 0 0 0/2 * * ?
new Env('StarNetwork挖矿')
"""
import requests

from utils.CommonUtil import get_proxy
from utils.StarNetworkUtil import get_headers, lock, main, log, is_restrict, StarNetwork


class StarNetworkMining(StarNetwork):
    def __init__(self):
        self.total_count = 0
        self.success_count = 0
        self.wait_count = 0
        self.fail_email = []

    def task(self, index, text, api_url):
        split = text.split('----')
        email = split[0]
        token = split[len(split) - 1]

        lock.acquire()
        self.total_count += 1
        lock.release()

        log.info(f"【{index}】{email}----正在挖矿")
        headers = get_headers(token)
        proxy = get_proxy(api_url)

        for i in range(3):
            try:
                resp = requests.post("https://apis.starnetwork.io/v3/session/start", headers=headers, timeout=15,
                                     proxies={"https": proxy})
                if resp.text.count('endAt') == 0:
                    if is_restrict(resp.text):
                        raise Exception('访问被拒绝')
                    raise Exception(resp.text)
                else:
                    lock.acquire()
                    if resp.text.count('NEW_SESSION_STARTED'):
                        log.info(f'【{index}】{email}----挖矿成功')
                        self.success_count += 1
                    else:
                        log.info(f'【{index}】{email}----挖矿时间未到')
                        self.wait_count += 1
                    lock.release()
                break
            except Exception as ex:
                if i != 2:
                    log.info(f'【{index}】{email}----进行第{i + 1}次重试----挖矿出错：{repr(ex)}')
                    proxy = get_proxy(api_url)
                else:
                    log.info(f'【{index}】{email}----重试完毕----挖矿出错：{repr(ex)}')
                    self.fail_email.append(f'【{index}】{email}----挖矿出错：{repr(ex)}')

    def statistics(self):
        if len(self.fail_email) > 0:
            log.info(f"-----Fail Statistics-----")
            log_data = ''
            for fail in self.fail_email:
                log_data += fail
            log.error(f'\n{log_data}')

    def save(self):
        pass

    def push_data(self):
        return f'总任务数：{self.total_count}\n任务成功数：{self.success_count}\n未到时间数：{self.wait_count}\n任务失败数：{len(self.fail_email)}'


if __name__ == '__main__':
    main("StarNetwork挖矿", StarNetworkMining(), 'StarNetworkToken')