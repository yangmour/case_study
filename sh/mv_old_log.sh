#!/bin/bash

# 定义需要处理的服务器列表（包含applogs目录下所有服务）
SERVERS=(
"demo"
)

# 获取当前年份和月份（强制十进制解析）
current_year=$(date +%Y)
current_month=$((10#$(date +%m)))

# 遍历服务器列表
for SERVER_NAME in "${SERVERS[@]}"; do
    echo "===== 开始处理 ${SERVER_NAME} 的日志 ====="

    # 1. 目录检测与适配
    local_log_with_logs="/nfs/develop/applogs/${SERVER_NAME}/logs"
    local_log_without_logs="/nfs/develop/applogs/${SERVER_NAME}"
    LOCAL_LOG_DIR=""
    OSS_BASE_PATH="oss://demo-logs/nfs/develop/applogs/${SERVER_NAME}"
    OSS_TARGET_PATH=""

    if [ -d "$local_log_with_logs" ]; then
        LOCAL_LOG_DIR="$local_log_with_logs"
        OSS_TARGET_PATH="${OSS_BASE_PATH}/logs"
        echo "→ 检测到带/logs的目录: $LOCAL_LOG_DIR"
    elif [ -d "$local_log_without_logs" ]; then
        LOCAL_LOG_DIR="$local_log_without_logs"
        OSS_TARGET_PATH="$OSS_BASE_PATH"
        echo "→ 检测到不带/logs的目录: $LOCAL_LOG_DIR"
    else
        echo "警告：两种日志目录都不存在，跳过 ${SERVER_NAME}"
        echo "===== ${SERVER_NAME} 的日志处理完成 ====="
        echo ""
        continue
    fi

    # 2. 进入日志目录
    cd "$LOCAL_LOG_DIR" || {
        echo "警告：无法进入目录 $LOCAL_LOG_DIR，跳过 ${SERVER_NAME}"
        echo "===== ${SERVER_NAME} 的日志处理完成 ====="
        echo ""
        continue
    }

    # 3. 筛选旧日志并按月份分组
    declare -A month_logs  # 关联数组：key=年月(2025-08)，value=日志文件列表
    old_log_count=0

    for log_file in *.log; do
        [ -f "$log_file" ] || continue  # 跳过非文件

        # 提取日志文件的年份和月份
        if [[ $log_file =~ ([0-9]{4})-([0-1][0-9])- ]]; then
            file_year=${BASH_REMATCH[1]}
            file_month_str=${BASH_REMATCH[2]}
            file_month=$((10#$file_month_str))
            file_ym="${file_year}-${file_month_str}"  # 年月标识：2025-08

            # 判断是否为前几个月的旧日志
            if [[ $file_year -lt $current_year ]] ||
               [[ $file_year -eq $current_year && $file_month -lt $current_month ]]; then
                month_logs["$file_ym"]+="$log_file "  # 按年月分组存储日志
                ((old_log_count++))
            fi
        fi
    done

    if [ $old_log_count -eq 0 ]; then
        echo "→ 没有需要处理的旧日志文件"
        echo "===== ${SERVER_NAME} 的日志处理完成 ====="
        echo ""
        continue
    fi
    echo "→ 共检测到 $old_log_count 个旧日志文件，按月份分组压缩"

    # 4. 按月份压缩并传输
    for ym in "${!month_logs[@]}"; do
        log_files=${month_logs["$ym"]}
        zip_name="${SERVER_NAME}-${ym}-logs.tar.gz"  # 压缩包命名：服务名-年月-logs.tar.gz

        echo -e "\n  处理 ${ym} 月份日志："
        echo "  涉及文件：$log_files"

        # 4.1 压缩日志文件（-z压缩，-c显示过程，-f指定压缩包）
        echo "  正在压缩为：$zip_name"
        tar -zcvf "$zip_name" $log_files 2>/dev/null  # 屏蔽tar的文件列表输出

        # 检查压缩是否成功
        if [ ! -f "$zip_name" ]; then
            echo "  ❌ 压缩 ${ym} 月份日志失败，跳过该月份"
            continue
        fi

        # 4.2 传输压缩包到OSS
        echo "  正在传输 $zip_name 到OSS"
        ossutil64 cp "$zip_name" "$OSS_TARGET_PATH/"

        # 4.3 验证传输结果，成功则清理本地文件
        if [ $? -eq 0 ]; then
            rm -f $log_files  # 删除原日志文件
            rm -f "$zip_name"  # 删除压缩包
            echo "  ✅ 成功：${ym} 月份日志压缩+传输完成，本地文件已清理"
        else
            rm -f "$zip_name"  # 传输失败，仅删除压缩包（保留原日志）
            echo "  ❌ 失败：$zip_name 传输到OSS失败，保留原日志文件"
        fi
    done

    echo -e "\n===== ${SERVER_NAME} 的日志处理完成 ====="
    echo ""
done

echo "所有服务器日志处理操作已结束"