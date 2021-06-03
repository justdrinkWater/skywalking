#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pika
from skywalking import config, agent
from skywalking.decorators import trace

from logger.LoggerUtil import LoggerUtil


@trace(op="do_print")
def do_print(st):
    do_print2(st)


@trace(op="do_print2")
def do_print2(st):
    print(st)


@trace(op="do_send_message")
def do_send_message(channel, record):
    channel.basic_publish(exchange='', routing_key='file_cdn_dev', body=str(record))


def send_message(message):
    # 新建连接，rabbitmq安装在本地则hostname为'localhost'
    credentials = pika.PlainCredentials('admin', 'finchina')  # mq用户名和密码
    hostname = '10.17.207.78'
    port = 5672
    virtual_host = '/'
    connection = pika.BlockingConnection(pika.ConnectionParameters(hostname, port, virtual_host, credentials))

    # 创建通道
    channel = connection.channel()
    # 声明一个队列，生产者和消费者都要声明一个相同的队列，用来防止万一某一方挂了，另一方能正常运行
    channel.queue_declare(queue='file_cdn_dev', arguments={"x-max-priority": 32}, durable=True)

    log = LoggerUtil()

    for record in message:
        # body = json.dumps(record)
        log.logger.info(record)
        do_send_message(channel, record)
    # 关闭连接
    connection.close()


if __name__ == '__main__':
    config.init(collector='10.15.97.6:11800', service='sunwei_dev')
    agent.start()
    message = [
        '[{"guid":"9E276DE5-067D-4AFF-A8A7-E47A6DC68EC7","filepath":"\\\\fileserver.finchina.local\\hct\\采购网\\中国比地招标网\\首页\\中标公告\\2019-08-19\\67baa6c0-a3d4-11ea-bc4a-9b431581c3d1.html","relativepath":"ZTB/HTML/2019/2019-08/2019-08-19/9E276DE5-067D-4AFF-A8A7-E47A6DC68EC7.html","filetype":"ZTBFile"}]']

    ret = send_message(message)
