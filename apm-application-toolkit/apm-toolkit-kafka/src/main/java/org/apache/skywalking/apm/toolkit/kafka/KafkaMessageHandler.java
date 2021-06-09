package org.apache.skywalking.apm.toolkit.kafka;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 该注解的作用是为了标记处理kafka消息的方法，方便增强对应的方法
 */
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface KafkaMessageHandler {


    /**
     * 操作名称，会作为span的名称
     */
    String operationName() default "";

    /**
     * 消息的类型
     */
    Class<?> messageClass();

    /**
     * 消息参数的位置，如果没有指定，则按照参数顺序匹配第一个类型一致的参数作为消息
     */
    int index() default 0;
}
