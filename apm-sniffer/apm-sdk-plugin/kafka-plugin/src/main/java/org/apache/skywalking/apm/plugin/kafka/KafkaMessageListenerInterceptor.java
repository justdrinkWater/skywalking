package org.apache.skywalking.apm.plugin.kafka;

import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.common.header.Header;
import org.apache.skywalking.apm.agent.core.context.CarrierItem;
import org.apache.skywalking.apm.agent.core.context.ContextCarrier;
import org.apache.skywalking.apm.agent.core.context.ContextManager;
import org.apache.skywalking.apm.agent.core.context.tag.Tags;
import org.apache.skywalking.apm.agent.core.context.trace.AbstractSpan;
import org.apache.skywalking.apm.agent.core.context.trace.SpanLayer;
import org.apache.skywalking.apm.agent.core.plugin.interceptor.enhance.EnhancedInstance;
import org.apache.skywalking.apm.agent.core.plugin.interceptor.enhance.InstanceMethodsAroundInterceptor;
import org.apache.skywalking.apm.agent.core.plugin.interceptor.enhance.MethodInterceptResult;
import org.apache.skywalking.apm.network.trace.component.ComponentsDefine;

import java.lang.reflect.Method;
import java.util.Iterator;
import java.util.Objects;

/**
 * @description 对Kafka消费消息的地方进行增强
 */
public class KafkaMessageListenerInterceptor implements InstanceMethodsAroundInterceptor {

    public static final String OPERATE_NAME_PREFIX = "Kafka/";
    public static final String CONSUMER_OPERATE_NAME = "/Consumer/";

    @Override
    public void beforeMethod(EnhancedInstance objInst, Method method, Object[] allArguments, Class<?>[] argumentsTypes, MethodInterceptResult result) throws Throwable {
        ConsumerRecord<?, ?> record = ((ConsumerRecord<?, ?>) allArguments[0]);
        ConsumerEnhanceRequiredInfo requiredInfo = extractEnhanceInfo(allArguments);
        AbstractSpan activeSpan = ContextManager.createEntrySpan(OPERATE_NAME_PREFIX + record.topic() + CONSUMER_OPERATE_NAME + (Objects.nonNull(requiredInfo) ? requiredInfo.getGroupId() : null), null)
                .start(System.currentTimeMillis());
        if (Objects.nonNull(requiredInfo)) {
            Tags.MQ_BROKER.set(activeSpan, requiredInfo.getBrokerServers());
        }
        Tags.MQ_TOPIC.set(activeSpan, record.topic());
        activeSpan.setComponent(ComponentsDefine.KAFKA_CONSUMER);
        SpanLayer.asMQ(activeSpan);
        ContextCarrier contextCarrier = new ContextCarrier();
        CarrierItem next = contextCarrier.items();
        while (next.hasNext()) {
            next = next.next();
            Iterator<Header> iterator = record.headers().headers(next.getHeadKey()).iterator();
            if (iterator.hasNext()) {
                next.setHeadValue(new String(iterator.next().value()));
            }
        }
        ContextManager.extract(contextCarrier);
    }

    /**
     * 从参数中获取ConsumerEnhanceRequiredInfo对象
     */
    private ConsumerEnhanceRequiredInfo extractEnhanceInfo(Object[] allArguments) {
        Object consumer = null;
        if (allArguments.length < 2 || allArguments.length > 3) {
            return null;
        }
        if (allArguments.length == 2) {
            consumer = allArguments[1];
        } else {
            consumer = allArguments[2];
        }
        if (consumer instanceof EnhancedInstance) {
            return (ConsumerEnhanceRequiredInfo) ((EnhancedInstance) consumer).getSkyWalkingDynamicField();
        }
        return null;
    }

    @Override
    public Object afterMethod(EnhancedInstance objInst, Method method, Object[] allArguments, Class<?>[] argumentsTypes, Object ret) throws Throwable {
        ContextManager.stopSpan();
        return ret;
    }

    @Override
    public void handleMethodException(EnhancedInstance objInst, Method method, Object[] allArguments, Class<?>[] argumentsTypes, Throwable t) {
        if (ContextManager.isActive()) {
            ContextManager.activeSpan().errorOccurred().log(t);
        }
    }
}
