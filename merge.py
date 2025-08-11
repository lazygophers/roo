import logging
import os
import re
from pathlib import Path

from rich.logging import RichHandler
from rich.progress import Progress
from ruamel.yaml import YAML

# --- 全局配置 ---

# 配置日志系统，使用 rich.logging.RichHandler 以获得格式优美的输出。
# 这使得日志更易于阅读，特别是在处理大量信息时。
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别为 INFO，只记录 INFO 及以上级别的消息
    handlers=[RichHandler(show_time=False)],  # 使用 RichHandler，不显示时间戳
    format="%(message)s"  # 日志格式仅包含消息本身
)
logger = logging.getLogger(__name__)  # 获取当前模块的 logger 实例

# 初始化 ruamel.yaml 实例，用于处理 YAML 文件。
# ruamel.yaml 是一个强大的库，可以保留 YAML 文件中的注释和格式。
yaml = YAML(pure=True)  # 使用纯 Python 实现，确保跨平台一致性
# yaml.default_flow_style = False  # 禁用流式风格，生成块状风格的 YAML，更易读
yaml.indent(mapping=2, sequence=4, offset=2)  # 设置缩进：字典4个空格，列表6个空格，列表内字典偏移3个空格


# --- 数据模型 ---

class CustomModel:
    """
    封装从 YAML 文件加载的自定义模型数据。

    这个类作为一个数据容器，提供了对模型核心属性（如 slug, source）的便捷访问。
    通过使用 @property，我们可以像访问普通属性一样调用方法，使代码更简洁。
    """

    def __init__(self, data: dict):
        """
        初始化 CustomModel 实例。

        Args:
            data (dict): 从 YAML 文件中解析出的原始字典数据。
        """
        self.data = data

    @property
    def slug(self) -> str | None:
        """
        获取模型的唯一标识符 (slug)。

        Returns:
            str | None: 模型的 slug，如果不存在则返回 None。
        """
        return self.data.get('slug')

    @property
    def source(self) -> str:
        """
        获取模型的来源。默认为 'global'。

        Returns:
            str: 模型的来源。
        """
        return self.data.get('source', 'global')

    @source.setter
    def source(self, value: str):
        """
        设置模型的来源。

        Args:
            value (str): 要设置的新来源值。
        """
        self.data['source'] = value


# ---核心处理函数 ---

def process_model(path: Path, before: str, after: str) -> CustomModel | None:
    """
    处理单个模型定义文件（YAML）。

    此函数执行以下操作：
    1. 读取并解析 YAML 文件。
    3. 将 `before` 和 `after` 的内容注入到 `customInstructions` 的前后。
    4. 设置模型的 `source` 和 `groups` 默认值。
    5. 验证处理后的数据是否包含所有必需的字段。
    6. 如果验证通过，返回一个 `CustomModel` 实例。

    Args:
        path (Path): 模型 YAML 文件的路径。
        before (str): 要添加到 `customInstructions` 开头的内容。
        after (str): 要添加到 `customInstructions` 结尾的内容。

    Returns:
        CustomModel | None: 如果处理和验证成功，则返回 CustomModel 实例；否则返回 None。
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.load(f)

        # 替换 customInstructions 中的代码片段占位符
        instructions = data.get('customInstructions', '')

        # 合并 before, instructions, 和 after 文本，形成最终的 customInstructions
        data['customInstructions'] = f"{before}\n\n---\n\n{instructions}\n\n---\n\n{after}"
        # 为模型设置固定的元数据
        data['source'] = 'global'
        # data['groups'] = ["read", "edit", "command", "browser", "mcp"]

        # 验证模型数据是否完整
        required_fields = ['slug', 'name', 'roleDefinition', 'customInstructions', 'whenToUse', 'description', 'groups']
        if any(field not in data for field in required_fields):
            logger.error(f"模型文件 {path} 缺少必要字段，已跳过。")
            return None

        return CustomModel(data)

    except Exception as e:
        logger.error(f"处理模型文件失败: {path} - {e}")
        return None


def write_output(models: list[CustomModel], output_path: Path):
    """
    将处理后的模型列表写入到单个 YAML 文件中。

    Args:
        models (list[CustomModel]): 要写入的 CustomModel 对象列表。
        output_path (Path): 输出的 YAML 文件路径。
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            # 将模型列表包装在一个字典中，以符合最终的 YAML 结构
            yaml.dump({"customModes": [m.data for m in models]}, f)
        logger.info(f"🎉 生成成功，所有模型已合并到: {output_path}")
    except Exception as e:
        logger.error(f"写入输出文件失败: {output_path} - {e}")


def run():
    """
    脚本的主执行函数。

    该函数协调整个流程：
    1. 定义并读取 `before.md` 和 `after.md` 嵌入文件。
    2. 加载所有代码片段。
    3. 查找所有待处理的模型 YAML 文件。
    4. 使用 `rich.progress` 创建一个进度条，可视化处理过程。
    5. 遍历并处理每个模型文件。
    6. 对处理后的模型列表进行排序，确保 `orchestrator` 模型始终位于首位。
    7. 将最终结果写入 `custom_models.yaml`。
    """
    # --- 路径定义 ---
    before_path = Path("models_hook/before.md")
    after_path = Path("models_hook/after.md")
    models_dir = Path("custom_models")
    output_file = Path("custom_models.yaml")

    # --- 文件加载 ---
    try:
        with open(before_path, 'r', encoding='utf-8') as f:
            before = f.read()
        with open(after_path, 'r', encoding='utf-8') as f:
            after = f.read()
    except Exception as e:
        logger.error(f"读取 before/after 嵌入文件失败: {e}")
        return  # 如果关键文件缺失，则终止执行

    model_paths = list(models_dir.rglob("*.yaml"))
    total_models = len(model_paths)

    if total_models == 0:
        logger.warning("在 'custom_models' 目录中未找到任何 .yaml 文件。")
        return

    # --- 模型处理 ---
    models = []
    with Progress() as progress:
        task = progress.add_task("[green]处理模型中...", total=total_models)
        for path in model_paths:
            logger.info(f"正在处理: {path.name}")
            model = process_model(path, before, after)
            if model:
                models.append(model)
            progress.advance(task)

    # --- 排序与输出 ---
    # 定义排序规则：'orchestrator' 类型的模型优先级最高，其他的按 slug 字母顺序排列。
    def sort_key(model: CustomModel):
        if model.slug == "orchestrator":
            return (0, model.slug)  # (0, ...) 会排在 (1, ...) 前面
        return (1, model.slug)

    models.sort(key=sort_key)
    write_output(models, output_file)


# --- 脚本入口 ---
if __name__ == "__main__":
    run()