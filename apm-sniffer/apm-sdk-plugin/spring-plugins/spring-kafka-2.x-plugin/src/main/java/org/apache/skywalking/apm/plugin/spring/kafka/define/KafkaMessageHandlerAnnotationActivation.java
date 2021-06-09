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

package org.apache.skywalking.apm.plugin.spring.kafka.define;

import net.bytebuddy.description.method.MethodDescription;
import net.bytebuddy.matcher.ElementMatcher;
import net.bytebuddy.matcher.ElementMatchers;
import org.apache.skywalking.apm.agent.core.plugin.interceptor.ConstructorInterceptPoint;
import org.apache.skywalking.apm.agent.core.plugin.interceptor.DeclaredInstanceMethodsInterceptPoint;
import org.apache.skywalking.apm.agent.core.plugin.interceptor.InstanceMethodsInterceptPoint;
import org.apache.skywalking.apm.agent.core.plugin.interceptor.enhance.ClassInstanceMethodsEnhancePluginDefine;
import org.apache.skywalking.apm.agent.core.plugin.match.ClassMatch;
import org.apache.skywalking.apm.agent.core.plugin.match.MethodAnnotationMatch;

import static net.bytebuddy.matcher.ElementMatchers.isAnnotatedWith;
import static net.bytebuddy.matcher.ElementMatchers.named;

/**
 * 增强加了{@link org.apache.skywalking.apm.toolkit.kafka.KafkaMessageHandler}注解的方法
 */
public class KafkaMessageHandlerAnnotationActivation extends ClassInstanceMethodsEnhancePluginDefine {

    public static final String TRACE_ANNOTATION_METHOD_INTERCEPTOR = "org.apache.skywalking.apm.plugin.spring.kafka.KafkaMessageHandlerAnnotationMethodInterceptor";
    public static final String TRACE_ANNOTATION = "org.apache.skywalking.apm.toolkit.kafka.KafkaMessageHandler";

    @Override
    public ConstructorInterceptPoint[] getConstructorsInterceptPoints() {
        return new ConstructorInterceptPoint[0];
    }

    @Override
    public InstanceMethodsInterceptPoint[] getInstanceMethodsInterceptPoints() {
        return new InstanceMethodsInterceptPoint[]{
                new DeclaredInstanceMethodsInterceptPoint() {
                    @Override
                    public ElementMatcher<MethodDescription> getMethodsMatcher() {
                        return ElementMatchers.isAnnotatedWith(ElementMatchers.named(TRACE_ANNOTATION));
                    }

                    @Override
                    public String getMethodsInterceptor() {
                        return TRACE_ANNOTATION_METHOD_INTERCEPTOR;
                    }

                    @Override
                    public boolean isOverrideArgs() {
                        return false;
                    }
                }
        };
    }

    @Override
    protected ClassMatch enhanceClass() {
        return MethodAnnotationMatch.byMethodAnnotationMatch(TRACE_ANNOTATION);
    }
}
