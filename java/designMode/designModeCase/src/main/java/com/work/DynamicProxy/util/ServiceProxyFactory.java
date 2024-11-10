package com.work.DynamicProxy.util;

import java.lang.reflect.Proxy;

/**
 * 代理工厂
 */
public class ServiceProxyFactory {

    public static <T> T getProxy(Class<T> interfaces,Class<?> clazzService) {
        return (T) Proxy.newProxyInstance(
                clazzService.getClassLoader(),
                new Class[]{interfaces},
                new ServiceProxyHandle(clazzService));
    }

    public static <T> T getProxy(Class<T> interfaces) {
        return (T) Proxy.newProxyInstance(
                interfaces.getClassLoader(),
                new Class[]{interfaces},
                new ServiceProxyHandle());
    }
}
