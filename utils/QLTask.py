from abc import ABCMeta, abstractmethod
from concurrent.futures import ThreadPoolExecutor

from notify import send
from utils.CommonUtil import log, load_txt, get_proxy_api, get_thread_number


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
    api_url = get_proxy_api(task_name)
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
