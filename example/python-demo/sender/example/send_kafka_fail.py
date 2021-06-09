# 发生消息失败
from skywalking import config, agent

from sender.sender import send_message

if __name__ == '__main__':
    config.init(collector='10.15.97.6:11800', service='sunwei_dev')
    agent.start()
    message = [
        '[{"guid": "8eb00075-91fd-4300-b5a5-a23a28bfbfb7","filepath": "\\\\fileserver.finchina.local\\hct\\债券公告\\2020-05-20\\货币网\\2254405.pdf","filetype":"Announmt_Bond"}]']

    ret = send_message(message)
