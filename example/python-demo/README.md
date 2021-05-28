# SkyWalking Python Agent
**SkyWalking-Python**: 是Apache SkyWalking的一个python版本，对python项目提供追踪能力

## 安装
### 安装python
**注意**：python需要3.5以上的版本 [下载](https://www.python.org/downloads/)

### 安装skywakling agent
#### From Pypi
python agent会打包上传到Pypi，所以可以使用pip命令来安装
```shell
# Install the latest version, using the default gRPC protocol to report data to OAP
pip install "apache-skywalking"

# Install the latest version, using the http protocol to report data to OAP
pip install "apache-skywalking[http]"

# Install the latest version, using the kafka protocol to report data to OAP
pip install "apache-skywalking[kafka]"

# Install a specific version x.y.z
# pip install apache-skywalking==x.y.z
pip install apache-skywalking==0.1.0  # For example, install version 0.1.0 no matter what the latest version is
```

#### From Source Codes
源码编译安装，可以参考[FAQ](https://github.com/apache/skywalking-python/blob/master/docs/FAQ.md#q-how-to-build-from-sources).

### 如何使用

```python
from skywalking import agent, config

config.init(collector='127.0.0.1:11800', service='your awesome service')
agent.start()
```
**注意**：python agent 需要skywalking服务端的版本在8.0以上，并且这里的初始化参数，请与相关人员进行沟通

#### Create Spans

以下代码演示如果创建span

```python
from skywalking import Component
from skywalking.trace.context import SpanContext, get_context
from skywalking.trace.tags import Tag

context: SpanContext = get_context()  # get a tracing context
# create an entry span, by using `with` statement,
# the span automatically starts/stops when entering/exiting the context
with context.new_entry_span(op='https://github.com/apache') as span:
    span.component = Component.Flask
# the span automatically stops when exiting the `with` context

with context.new_exit_span(op='https://github.com/apache', peer='localhost:8080') as span:
    span.component = Component.Flask

with context.new_local_span(op='https://github.com/apache') as span:
    span.tag(Tag(key='Singer', val='Nakajima'))
```

#### Decorators

```python
from time import sleep

from skywalking import Component
from skywalking.decorators import trace, runnable
from skywalking.trace.context import SpanContext, get_context
from skywalking.trace.ipc.process import SwProcess

@trace()  # the operation name is the method name('some_other_method') by default
def some_other_method():
    sleep(1)


@trace(op='awesome')  # customize the operation name to 'awesome'
def some_method():
    some_other_method()


@trace(op='async_functions_are_also_supported')
async def async_func():
    return 'asynchronous'


@trace()
async def async_func2():
    return await async_func()


@runnable() # cross thread propagation
def some_method(): 
    some_other_method()

from threading import Thread 
t = Thread(target=some_method)
t.start()

# When another process is started, agents will also be started in other processes, 
# supporting only the process mode of spawn.
p1 = SwProcess(target=some_method) 
p1.start()
p1.join()


context: SpanContext = get_context()
with context.new_entry_span(op=str('https://github.com/apache/skywalking')) as span:
    span.component = Component.Flask
    some_method()
```
