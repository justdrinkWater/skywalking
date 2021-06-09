from skywalking import agent, config

from collector.mysql_collector import get_data, FileCdnRecord
from sender.sender import send_message

if __name__ == '__main__':
    # 加载skywalking
    config.init(collector='10.15.97.6:11800', service='python_collector_dev')
    agent.start()

    # 抓取数据
    ret = get_data(FileCdnRecord.id < 100)

    # 发生数据到mq
    send_message(ret)
