package org.apache.skywalking.apm.plugin.spring.kafka;

import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.common.header.Headers;
import org.apache.skywalking.apm.agent.core.context.ContextManager;
import org.apache.skywalking.apm.agent.core.plugin.interceptor.enhance.EnhancedInstance;
import org.apache.skywalking.apm.agent.core.plugin.interceptor.enhance.InstanceMethodsAroundInterceptor;
import org.apache.skywalking.apm.agent.core.plugin.interceptor.enhance.MethodInterceptResult;

import java.lang.reflect.Method;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;


/**
 * 对批量文件处理进行增强
 **/
public class KafkaBatchMessageListenerInterceptor implements InstanceMethodsAroundInterceptor {

    public static final String KAFKA_BATCH_MESSAGE_KEY = "KAFKA_BATCH_MESSAGE_KEY";

    @SuppressWarnings("unchecked")
    @Override
    public void beforeMethod(EnhancedInstance objInst, Method method, Object[] allArguments, Class<?>[] argumentsTypes, MethodInterceptResult result) throws Throwable {
        ContextManager.createLocalSpan("/spring-kafka/onBatchMessage");
        //将kafka消息缓存到线程上下文
        List<ConsumerRecord<?, ?>> records = ((List<ConsumerRecord<?, ?>>) allArguments[0]);
        if (!records.isEmpty()) {
            Map<?, Headers> recordHeadersMap = records.stream().collect(Collectors.toMap(ConsumerRecord::value, ConsumerRecord::headers));
            ContextManager.getRuntimeContext().put(KAFKA_BATCH_MESSAGE_KEY, recordHeadersMap);
            ContextManager.getCorrelationContext().putCustomerData(KAFKA_BATCH_MESSAGE_KEY, recordHeadersMap);
        }
    }

    @Override
    public Object afterMethod(EnhancedInstance objInst, Method method, Object[] allArguments, Class<?>[] argumentsTypes, Object ret) throws Throwable {
        //消费方法结束，清楚上下文中的消息
        ContextManager.stopSpan();
        return ret;
    }

    @Override
    public void handleMethodException(EnhancedInstance objInst, Method method, Object[] allArguments, Class<?>[] argumentsTypes, Throwable t) {
        ContextManager.getRuntimeContext().remove(KAFKA_BATCH_MESSAGE_KEY);
        ContextManager.activeSpan().errorOccurred().log(t);
    }
}
