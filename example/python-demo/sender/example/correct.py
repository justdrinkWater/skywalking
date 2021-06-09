# 成功消息
from skywalking import config, agent

from sender.sender import send_message

if __name__ == '__main__':
    config.init(collector='10.15.97.6:11800', service='sunwei_dev')
    agent.start()
    message = ['{\"filepath\":"\\\\\\\\fileserver.finchina.local\\\\hct\\\\test\\\\court_annount\\\\2020\\\\09\\\\03\\\\48FD7ECB-E593-4A0A-826B-2912E07F3C49.html","filetype":"rmfygg_daily","guid":"48FD7ECB-E593-4A0A-826B-2912E07F3C49","relativepath":"rmfygg/2020/09/03/48FD7ECB-E593-4A0A-826B-2912E07F3C49.html"}']

    ret = send_message(message)
