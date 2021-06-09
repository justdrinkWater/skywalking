/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

package org.apache.skywalking.apm.plugin.spring.kafka;

import org.apache.kafka.common.header.Header;
import org.apache.kafka.common.header.Headers;
import org.apache.skywalking.apm.agent.core.context.CarrierItem;
import org.apache.skywalking.apm.agent.core.context.ContextCarrier;
import org.apache.skywalking.apm.agent.core.context.ContextManager;
import org.apache.skywalking.apm.agent.core.context.tag.StringTag;
import org.apache.skywalking.apm.agent.core.context.trace.AbstractSpan;
import org.apache.skywalking.apm.agent.core.context.trace.SpanLayer;
import org.apache.skywalking.apm.agent.core.plugin.interceptor.enhance.EnhancedInstance;
import org.apache.skywalking.apm.agent.core.plugin.interceptor.enhance.InstanceMethodsAroundInterceptor;
import org.apache.skywalking.apm.agent.core.plugin.interceptor.enhance.MethodInterceptResult;
import org.apache.skywalking.apm.agent.core.util.MethodUtil;
import org.apache.skywalking.apm.network.trace.component.ComponentsDefine;
import org.apache.skywalking.apm.toolkit.kafka.KafkaMessageHandler;

import java.lang.reflect.Method;
import java.util.Iterator;
import java.util.Map;
import java.util.Objects;

import static org.apache.skywalking.apm.plugin.spring.kafka.KafkaBatchMessageListenerInterceptor.KAFKA_BATCH_MESSAGE_KEY;

/**
 * 对处理方法进行增强
 */
public class KafkaMessageHandlerAnnotationMethodInterceptor implements InstanceMethodsAroundInterceptor {

    @SuppressWarnings("unchecked")
    @Override
    public void beforeMethod(EnhancedInstance objInst, Method method, Object[] allArguments, Class<?>[] argumentsTypes,
                             MethodInterceptResult result) throws Throwable {
        KafkaMessageHandler annotation = method.getAnnotation(KafkaMessageHandler.class);
        //1、获取到方法的消息参数
        Object message = extractMessageArgument(argumentsTypes, allArguments, annotation);
        //2、从线程上下文对象中获取到消息map
        Map<?, Headers> recordHeadersMap = (Map<?, Headers>) ContextManager.getRuntimeContext().get(KAFKA_BATCH_MESSAGE_KEY);
        //3、获取到消息header
        Headers headers = recordHeadersMap.get(message);
        //4、放入上下文中
        String operationName = annotation.operationName();
        if (Objects.nonNull(headers)) {
            AbstractSpan localSpan = ContextManager.createLocalSpan(operationName.length() == 0 ? MethodUtil.generateOperationName(method) : operationName);
            localSpan.setComponent(ComponentsDefine.KAFKA_CONSUMER);
            SpanLayer.asMQ(localSpan);
            localSpan.tag(new StringTag("value"), message.toString());
            ContextCarrier contextCarrier = new ContextCarrier();
            CarrierItem next = contextCarrier.items();
            while (next.hasNext()) {
                next = next.next();
                Iterator<Header> iterator = headers.headers(next.getHeadKey()).iterator();
                if (iterator.hasNext()) {
                    next.setHeadValue(new String(iterator.next().value()));
                }
            }
            ContextManager.extract(contextCarrier);
        }
    }

    /**
     * 找到消息参数
     */
    private Object extractMessageArgument(Class<?>[] argumentsTypes, Object[] allArguments, KafkaMessageHandler annotation) {
        int index = annotation.index();
        Class<?> messageClass = annotation.messageClass();
        //如果指定了index，并且index位置的类型与指定的类型一致，返回index位置的参数
        if (argumentsTypes.length >= index && argumentsTypes[index] == messageClass) {
            return allArguments[index];
        }
        //循环遍历找到类型一致的参数
        for (int i = 0; i < argumentsTypes.length; i++) {
            if (argumentsTypes[i] == messageClass)
                return allArguments[i];
        }
        return null;
    }

    @SuppressWarnings("unchecked")
    @Override
    public Object afterMethod(EnhancedInstance objInst, Method method, Object[] allArguments, Class<?>[] argumentsTypes,
                              Object ret) throws Throwable {
        if (ContextManager.isActive()) {
            Map<?, Headers> recordHeadersMap = (Map<?, Headers>) ContextManager.getRuntimeContext().get(KAFKA_BATCH_MESSAGE_KEY);
            ContextManager.stopSpan();
            ContextManager.getRuntimeContext().put(KAFKA_BATCH_MESSAGE_KEY, recordHeadersMap);
        }
        return ret;
    }

    @Override
    public void handleMethodException(EnhancedInstance objInst, Method method, Object[] allArguments,
                                      Class<?>[] argumentsTypes, Throwable t) {
        if (ContextManager.isActive()) {
            ContextManager.activeSpan().errorOccurred().log(t);
        }
    }
}
