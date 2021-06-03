# -*- coding:utf-8 -*-
import json

import pika


class sendRabbitMQTool(object):
    def __init__(self, queueName, priority, environment='dev', is_parse=True):
        self.queueName = queueName
        self.priority = priority
        if environment == 'dev':
            __username = 'admin'
            __password = 'finchina'
            hosts = ['10.17.207.61', '10.17.207.78', '10.17.207.94']
            port = 5672
        elif environment == 'product':
            __username = 'admin'
            __password = 'FINchina2020'
            hosts = ['10.55.10.100', '10.55.10.101', '10.55.10.102']
            port = 5678
        else:
            return

        __userinfo = pika.PlainCredentials(__username, __password)
        parameters = (
            pika.ConnectionParameters(host=hosts[0], port=port, connection_attempts=5, retry_delay=1,
                                      credentials=__userinfo),
            pika.ConnectionParameters(host=hosts[1], port=port, connection_attempts=5, retry_delay=1,
                                      credentials=__userinfo),
            pika.ConnectionParameters(host=hosts[2], port=port, connection_attempts=5, retry_delay=1,
                                      credentials=__userinfo)
        )
        self.__connection = pika.BlockingConnection(parameters)
        self.__channel = self.__connection.channel()  # 生成管道，在管道里跑不同的队列
        if is_parse:
            self.__channel.queue_declare(queue=self.queueName, durable=True)
        else:
            self.__channel.queue_declare(queue=self.queueName, durable=True, arguments={'x-max-priority': 32})

    def send_object(self, object, ensure_ascii=False):
        try:
            content = json.dumps(object, ensure_ascii=ensure_ascii)
            self.__channel.basic_publish(exchange='', routing_key=self.queueName, body=str(content),
                                         properties=pika.BasicProperties(delivery_mode=2,
                                                                         priority=self.priority))  # 历史数据消息等级2 ，日常消息等级15
        except Exception as e:
            return False
        else:
            return True

    def send_json(self, jsonStr):
        try:
            self.__channel.basic_publish(exchange='', routing_key=self.queueName, body=str(jsonStr),
                                         properties=pika.BasicProperties(delivery_mode=2,
                                                                         priority=self.priority))  # 历史数据消息等级2 ，日常消息等级15
        except Exception as e:
            return False
        else:
            return True
