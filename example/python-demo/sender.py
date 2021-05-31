#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random

import pika
from skywalking import agent, config
from skywalking.decorators import trace

config.init(collector='127.0.0.1:11800', service='sunwei_dev')
agent.start()


@trace(op="do_print")
def do_print(st):
    do_print2(st)


@trace(op="do_print2")
def do_print2(st):
    print(st)


@trace(op="send_message")
def send_message():
    # 新建连接，rabbitmq安装在本地则hostname为'localhost'
    credentials = pika.PlainCredentials('admin', 'finchina')  # mq用户名和密码
    hostname = '10.17.207.78'
    port = 5672
    virtual_host = '/'
    connection = pika.BlockingConnection(pika.ConnectionParameters(hostname, port, virtual_host, credentials))

    # 创建通道
    channel = connection.channel()
    # 声明一个队列，生产者和消费者都要声明一个相同的队列，用来防止万一某一方挂了，另一方能正常运行
    channel.queue_declare(queue='sunwei_sw_queue_demo', durable=True)

    message = {
        'id': random.randint(1, 1000)
    }
    body = json.dumps(message)

    do_print(body)

    # 发送消息到mq
    channel.basic_publish(exchange='EXCHANGE_DEMO_', routing_key='ROUTING_KEY_', body=body,
                          properties=pika.BasicProperties(content_type='text'))

    do_print(body)
    # 关闭连接
    connection.close()


send_message()
