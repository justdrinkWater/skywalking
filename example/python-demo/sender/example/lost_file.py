# 丢失文件异常
from skywalking import config, agent

from sender.sender import send_message

if __name__ == '__main__':
    config.init(collector='10.15.97.6:11800', service='sunwei_dev')
    agent.start()
    message = [
        '[{"guid": "5B5F032B-AC09-4870-9B07-89F4807EF073", "filepath": "\\\\\\\\fileserver.finchina.local\\\\外网文件\\\\文书网\\\\2020\\\\01\\\\03\\\\5B5F032B-AC09-4870-9B07-89F4807EF073.html", "relativepath": "2020/01/03/5B5F032B-AC09-4870-9B07-89F4807EF073.html", "filetype": "judgmentfile_daily"}]']

    ret = send_message(message)
