# -*- coding:utf-8 -*-
import json
import math
import time
from datetime import datetime

import pika
import pymysql
from apscheduler.schedulers.blocking import BlockingScheduler


def job(host, port, user, password, database, queue_name):
    print('job start at : ', datetime.now())
    # 从文件中读取index
    fp = open('index.txt')
    index = fp.readline()
    index_info = index

    # 定义发送对象
    a = sendRabbitMQTool(queue_name, 11)

    # 从数据库读取数据
    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset='utf8',
        use_unicode=True,
    )
    cur = conn.cursor()
    # 先查询当前的时刻比上一次查询多了多少数据
    sql_count = "select max(id) from file_cdn_record_202108"
    cur.execute(sql_count)
    info = cur.fetchall()
    # 多了多少个
    max_id = info[0][0]
    print('最大id----', max_id)
    # 切分1000条请求一次 向上取值, 不足1000，算一次
    times = math.ceil((max_id - int(index)) / 1000)
    if times >= 1:
        for time in range(times):  # time从0开始
            sql_query = "select id, message from file_cdn_record_202108 where id > " + str(
                index) + "  and state != 9 and (filepath like '%html' or filepath like 'htm' or filepath like '%json') order by id asc limit 1000"
            # 递增
            index = int(index) + 1000
            print('查询sql----', sql_query)
            cur.execute(sql_query)  # 默认不返回查询结果集， 返回数据记录数。
            info = cur.fetchall()  # 获取所有的查询结果
            print('查询结果个数----', len(info))
            for item in info:
                # 记录index
                index_info = item[0]
                # 写入到rabbitmq
                a.send_json(item[1].replace('\'', '\"'))

        # 将id写入到文件
        print('写入文件的index----', index_info)
        with open(
                'index.txt',
                'r+',
                encoding='utf-8') as f1:
            f1.write(str(index_info))
    # 关闭连接
    cur.close()
    conn.close()
    print('job end at : ', datetime.now())


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
            self.__channel.queue_declare(queue=self.queueName, durable=True, arguments={'x-max-priority': 32})
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


def example(host, port, user, password, database):
    print('start : ', datetime.now())
    print(host, str(port), user, password, database)
    time.sleep(11)
    print('end : ', datetime.now())


if __name__ == '__main__':
    # 创建定时任务，阻塞队列执行，这里的任务不会覆盖执行，即如果第一个任务的执行时间已经超过了第二个任务的开始时间，那个第二个任务不会执行，而是放弃第二个任务，
    # 如果第一个任务的执行时间超过了第三个任务的开始时间，那么第三个任务也会放弃，直到第一个任务执行结束，后续的任务才会开始执行，任务的执行时间间隔30分钟
    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'interval', minutes=30, start_date='2021-08-16 15:52:20',
                      args=['10.17.207.71', 3306, 'root', '123456', 'file_pre_handle_dev', 'file_pre_handle_tes'])
    scheduler.start()
