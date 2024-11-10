package com.work.DynamicProxy.util;

import com.alibaba.fastjson2.JSON;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.Arrays;


/**
 * 代理对象处理器
 */
public class ServiceProxyHandle implements InvocationHandler {

    private final Logger log = LoggerFactory.getLogger(ServiceProxyHandle.class);
    // 真正实例clazz对象
    private Class<?> clazz;

    public ServiceProxyHandle() {
    }

    public ServiceProxyHandle(Class<?> clazz) {
        this.clazz = clazz;
    }

    /**
     * @param proxy 代理对象
     * @param method 方法信息
     * @param args 方法参数     *
     * @return
     * @throws Throwable
     */
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        log.info("动态代理执行器开始!");
        log.info("proxy={},method={},args={}", JSON.toJSONString(proxy), JSON.toJSONString(method), Arrays.toString(args));
        log.info("clazz={}", JSON.toJSONString(clazz.getName()));

        if (clazz == null){
            return null;
        }
        //动态代理真正调用执行方法
        Object resp = invokeBean(clazz,proxy, method, args);

        log.info("动态代理执行器结束resp={}!", JSON.toJSONString(resp));
        return resp;
    }

    /**
     * 动态代理真正调用执行方法
     * @param clazz 真正的实例
     * @param proxy 代理对象
     * @param method 方法信息
     * @param args 方法参数
     * @return
     * @throws NoSuchMethodException
     * @throws InvocationTargetException
     * @throws IllegalAccessException
     * @throws InstantiationException
     */
    private Object invokeBean(Class<?> clazz, Object proxy, Method method, Object[] args) throws NoSuchMethodException, InvocationTargetException, IllegalAccessException, InstantiationException {
        Constructor<?> declaredConstructor = clazz.getDeclaredConstructor();
        declaredConstructor.setAccessible(true);
        Object newInstance = declaredConstructor.newInstance();
        Method clazzMethod;
        if (args == null || args.length == 0) {
            clazzMethod = clazz.getMethod(method.getName());
        }else {
            Class<?>[] argTypes = new Class[args.length];
            for (int i = 0; i < args.length; i++) {
                argTypes[i] = args[i].getClass();
            }
            clazzMethod = clazz.getMethod(method.getName(), argTypes);
        }
        log.info("执行器过程");
        Object invoke = clazzMethod.invoke(newInstance, args);
        return invoke;
    }
}
