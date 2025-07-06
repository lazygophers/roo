import os
import yaml  # 新增YAML模块

from core.logger import log


# 新增配置加载逻辑
def load_config():
    config_path = os.path.join(os.getcwd(), "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


config = load_config()

log.info("load config {}".format(config))

# 从配置文件读取变量
app_name = str(config["app_name"]) if config["app_name"] else "lazygophers"
http_port = int(config["http_port"]) if config["http_port"] else 14000
searx_hosts = list(config["searx_hosts"]) if config["searx_hosts"] else []
debug = bool(config["debug"]) if config["debug"] else False

cache_dir = os.path.join(os.getcwd(), "cache")

os.environ["COQUI_TOS_AGREED"] = "1"

if debug:
    log.setLevel("DEBUG")
else:
    log.setLevel("INFO")