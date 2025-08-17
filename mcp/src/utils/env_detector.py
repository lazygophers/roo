import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_running_in_docker() -> bool:
    """
    准确判断当前应用是否在 Docker 容器内运行。

    通过两种可靠的方法进行检测：
    1. 检查根目录下是否存在 `.dockerenv` 文件。
       这是 Docker 环境中一个常见的标识文件。
    2. 检查 `/proc/1/cgroup` 文件内容是否包含 "docker" 关键词。
       在 Linux 系统中，cgroup 信息可以揭示进程的运行环境。

    :return: 如果在 Docker 容器中运行，则返回 True，否则返回 False。
    """
    # 方法一：检查 /.dockerenv 文件是否存在
    if os.path.exists('/.dockerenv'):
        logging.info("检测到 /.dockerenv 文件，确认为 Docker 环境。")
        return True

    # 方法二：检查 /proc/1/cgroup 文件内容
    try:
        with open('/proc/1/cgroup', 'rt') as f:
            cgroup_content = f.read()
            if 'docker' in cgroup_content:
                logging.info("在 /proc/1/cgroup 中检测到 'docker' 关键字，确认为 Docker 环境。")
                return True
    except FileNotFoundError:
        # 如果文件不存在，说明不是一个标准的 Linux 环境，可能不是 Docker
        logging.debug("/proc/1/cgroup 文件未找到，跳过该检测方法。")
        pass
    except Exception as e:
        logging.error(f"读取 /proc/1/cgroup 文件时发生未知错误: {e}")
        pass

    logging.info("未检测到 Docker 环境特征。")
    return False

if __name__ == '__main__':
    # 一个简单的测试，用于直接运行此脚本时验证函数功能
    in_docker = is_running_in_docker()
    print(f"当前是否在 Docker 容器中运行: {in_docker}")
