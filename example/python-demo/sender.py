#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pika
import random
from skywalking import agent, config

config.init(collector='10.15.97.6:11800', service='sunwei_dev')
agent.start()
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

id = random.randint(1, 1000)
message = {
    'id': id
}
body = json.dumps(message)

print(body)
# 发送消息到mq
channel.basic_publish(exchange='EXCHANGE_DEMO_', routing_key='ROUTING_KEY_', body=body,
                      properties=pika.BasicProperties(content_type='text'))
# 关闭连接
connection.close()
