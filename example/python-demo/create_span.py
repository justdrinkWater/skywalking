#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from skywalking import Component, config, agent
from skywalking.trace.context import SpanContext, get_context
from skywalking.trace.tags import Tag

config.init(collector='10.15.97.6:11800', service='sunwei_dev')
agent.start()

context: SpanContext = get_context()  # get a tracing context
# create an entry span, by using `with` statement,
# the span automatically starts/stops when entering/exiting the context
with context.new_entry_span(op='https://github.com/apache') as span:
    span.component = Component.Flask

with context.new_local_span(op='https://github.com/apache') as span:
    span.tag(Tag(key='Singer', val='Nakajima'))

# the span automatically stops when exiting the `with` context
with context.new_exit_span(op='https://github.com/apache', peer='localhost:8080') as span:
    span.component = Component.Flask
