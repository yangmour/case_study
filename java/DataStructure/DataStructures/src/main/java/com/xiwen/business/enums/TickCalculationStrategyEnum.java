package com.xiwen.business.enums;

import java.util.function.BiFunction;

/**
 * 刻度计算策略枚举（类名后缀加Enum，明确标识枚举类型）
 * 继承自 java.lang.Enum，支持枚举特性（如name()、ordinal()、valueOf()等）
 */
public enum TickCalculationStrategyEnum {

    /**
     * 原始方式（直接取整）
     * 特点：能早不晚，可能提前执行，偏差范围 [0, -tickDuration]
     * 适用场景：允许提前、对偏差不敏感的非关键任务（如日志定时备份）
     */
    ORIGINAL(
            "原始方式（直接取整）",
            (delayMs, tickDuration) -> delayMs / tickDuration,  // 核心逻辑：直接除法取整
            "允许提前执行，实现简单，适合非关键任务（如日志清理）"
    ),

    /**
     * 四舍五入方式
     * 特点：不偏不倚，偏差均匀分布 [-tickDuration/2, +tickDuration/2]
     * 适用场景：对提前/延后无限制、需偏差稳定的通用场景（如定时消息推送）
     */
    ROUND_HALF_UP(
            "四舍五入方式",
            (delayMs, tickDuration) -> (delayMs + tickDuration / 2) / tickDuration,  // 核心逻辑：加半取整
            "偏差均匀，兼顾精度与性能，适合多数通用场景（如通知推送）"
    ),

    /**
     * 向上取整方式
     * 特点：能晚不早，绝对不提前，偏差范围 [0, +tickDuration]
     * 适用场景：严格不允许提前的关键任务（如订单超时取消、金融结算）
     */
    UPWARD_ROUNDING(
            "向上取整方式",
            (delayMs, tickDuration) -> (delayMs + tickDuration - 1) / tickDuration,  // 核心逻辑：加间隔-1取整
            "绝对不提前，安全性高，适合关键任务（如订单取消、支付超时）"
    );

    // 枚举自定义属性：补充枚举常量的业务信息
    private final String displayName;    // 易读的展示名称（区别于默认的name()）
    private final BiFunction<Long, Long, Long> ticksCalculator;  // 刻度计算逻辑（函数式接口，简化代码）
    private final String scenarioDesc;   // 适用场景描述（便于开发时选择）

    /**
     * 构造函数（Enum父类默认传入name和ordinal，无需显式定义）
     * @param displayName 展示名称
     * @param ticksCalculator 计算逻辑
     * @param scenarioDesc 场景描述
     */
    TickCalculationStrategyEnum(String displayName, BiFunction<Long, Long, Long> ticksCalculator, String scenarioDesc) {
        this.displayName = displayName;
        this.ticksCalculator = ticksCalculator;
        this.scenarioDesc = scenarioDesc;
    }

    /**
     * 核心方法：计算任务应分配的刻度数（对外提供统一调用入口）
     * @param delayMs 任务总延迟时间（毫秒）
     * @param tickDuration 时间轮刻度间隔（毫秒）
     * @return 最终刻度数
     */
    public long calculateTicks(long delayMs, long tickDuration) {
        // 参数合法性校验：避免无效输入导致业务异常
        if (delayMs < 0) {
            throw new IllegalArgumentException("延迟时间不能为负数（当前delayMs=" + delayMs + "）");
        }
        if (tickDuration <= 0) {
            throw new IllegalArgumentException("刻度间隔必须为正数（当前tickDuration=" + tickDuration + "）");
        }
        // 调用当前枚举常量的计算逻辑
        return ticksCalculator.apply(delayMs, tickDuration);
    }

    // -------------------------- Enum 特性相关方法 --------------------------
    /**
     * 重写toString()：返回易读的展示名称（默认返回name()，如"ORIGINAL"）
     */
    @Override
    public String toString() {
        return displayName;
    }

    /**
     * 通过枚举名称获取实例（封装Enum.valueOf()，增加异常提示）
     * @param name 枚举名称（如"UPWARD_ROUNDING"）
     * @return 对应的枚举实例
     */
    public static TickCalculationStrategyEnum getByName(String name) {
        try {
            return TickCalculationStrategyEnum.valueOf(name);
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("无效的刻度计算策略名称：" + name + 
                    "，可选值为：" + getAvailableNames(), e);
        }
    }

    /**
     * 获取所有枚举名称（用于日志或配置校验）
     */
    public static String getAvailableNames() {
        StringBuilder sb = new StringBuilder();
        for (TickCalculationStrategyEnum strategy : values()) {
            sb.append(strategy.name()).append("、");
        }
        return sb.deleteCharAt(sb.length() - 1).toString();
    }

    // -------------------------- Getter 方法（封装属性，避免直接访问） --------------------------
    public String getDisplayName() {
        return displayName;
    }

    public String getScenarioDesc() {
        return scenarioDesc;
    }
}