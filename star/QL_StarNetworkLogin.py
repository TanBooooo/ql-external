"""
cron: 1 1 1 1 * ?
new Env('StarNetwork登录')
"""
import requests

from utils.QLTask import main, QLTask
from utils.CommonUtil import log, lock, get_proxy, write_txt
from utils.StarNetworkUtil import get_headers, encrypt_hash, is_exception


class StarNetworkLogin(QLTask):
    def __init__(self):
        self.total_count = 0
        self.success_email = []
        self.blocked_email = []
        self.fail_email = []

    def task(self, index, text, api_url):
        split = text.split('----')
        email = split[0]
        password = split[1]

        lock.acquire()
        self.total_count += 1
        lock.release()

        log.info(f"【{index}】{email}----正在登录")
        headers = get_headers()
        proxy = get_proxy(api_url)
        payload = encrypt_hash({"email": email, "password": password})

        for i in range(3):
            try:
                resp = requests.post("https://api.starnetwork.io/v3/email/login_check", json=payload, headers=headers,
                                     proxies={"https": proxy}, timeout=15)
                is_exception(resp.text)

                if resp.text.count('jwt') == 0:
                    raise Exception(resp.text)

                if resp.json()['status'] == 'blocked':
                    log.error(f'【{index}】{email}----账号封禁')
                    self.blocked_email.append(f'{email}----{password}')

                if resp.json()['status'] == 'registered':
                    token = resp.json()['jwt']
                    log.info(f'【{index}】{email}----登录成功')
                    headers['Authorization'] = "Bearer {}".format(token)
                    resp = requests.get('https://api.starnetwork.io/v3/auth/user', headers=headers, timeout=15,
                                        proxies={"https": proxy})
                    if resp.text.count('{"id":') > 0:
                        uid = resp.json()['id']
                        log.info(f'【{index}】{email}----ID获取成功')
                        self.success_email.append(f'{email}----{password}----{uid}----{token}')
                    else:
                        if is_exception(resp.text):
                            raise Exception('访问被拒绝')
                        raise Exception(resp.text)
                break
            except Exception as ex:
                if repr(ex).count('账号被封禁或登录失效') > 0:
                    log.info(f'【{index}】{email}----账号被封禁或登录失效')
                    return

                if i != 2:
                    log.info(f'【{index}】{email}----进行第{i + 1}次重试----登录出错：{repr(ex)}')
                    proxy = get_proxy(api_url)
                else:
                    log.info(f'【{index}】{email}----重试完毕----登录出错：{repr(ex)}')
                    self.fail_email.append(f'【{index}】{email}----{password}----登录出错：{repr(ex)}')
                    break

    def statistics(self):
        if len(self.blocked_email) > 0:
            log.info(f"-----Blocked Statistics-----")
            log_data = ''
            for blocked in self.blocked_email:
                log_data += blocked + '\n'
            log.error(f'\n{log_data}')

        if len(self.fail_email) > 0:
            log.info(f"-----Fail Statistics-----")
            log_data = ''
            for fail in self.fail_email:
                log_data += fail + '\n'
            log.error(f'\n{log_data}')

    def save(self):
        write_txt("StarNetwork", '')
        if len(self.success_email) > 0:
            log.info(f"-----Save Success-----")
            for success in self.success_email:
                write_txt("StarNetworkToken", success + '\n', True)
        if len(self.blocked_email) > 0:
            log.info(f"-----Save Blocked-----")
            for blocked in self.blocked_email:
                write_txt("StarNetwork已封禁", blocked + '\n', True)
        if len(self.fail_email) > 0:
            log.info(f"-----Save Fail-----")
            for fail in self.fail_email:
                write_txt("StarNetwork登录失败", fail + '\n', True)

    def push_data(self):
        return f'总任务数：{self.total_count}\n任务成功数：{len(self.success_email)}\n账号封禁数：{len(self.blocked_email)}\n任务失败数：{len(self.fail_email)}',


if __name__ == '__main__':
    login = StarNetworkLogin()
    main("StarNetwork登录", StarNetworkLogin(), 'StarNetwork')
