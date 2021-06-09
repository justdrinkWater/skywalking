# -*- coding:utf-8 -*-
import time
from datetime import datetime
from time import sleep

import requests


def send_http(url):
    # 以下为GET请求
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    request = requests.get(url)
    print(request.content)  # 返回字节形式


i = 1
while i > 0:
    send_http('http://localhost:8079/demo/rabbitmq')
    i = i - 1
    sleep(1)
