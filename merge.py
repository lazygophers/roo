import logging
import os
from pathlib import Path
from rich.logging import RichHandler
from rich.progress import Progress
from ruamel.yaml import YAML

# 配置日志（使用rich日志处理器）
logging.basicConfig(
    level=logging.INFO,
    handlers=[RichHandler(show_time=False)],
    format="%(message)s"
)
logger = logging.getLogger(__name__)

yaml = YAML(pure=True)
yaml.default_flow_style = False
yaml.indent(mapping=4, sequence=6, offset=3)


class CustomModel:
    def __init__(self, data):
        self.data = data

    @property
    def slug(self):
        return self.data.get('slug')

    @property
    def source(self):
        return self.data.get('source', 'global')

    @source.setter
    def source(self, value):
        self.data['source'] = value


def load_code_snippets(root: Path) -> dict:
    code_snippet_map = {}
    for root_dir, _, files in os.walk(root):
        for file in files:
            if file.endswith(".md"):
                path = Path(root_dir) / file
                key = path.stem
                try:
                    with open(path, 'r') as f:
                        content = f.read()
                        if not content.endswith('\n'):
                            content += '\n'
                        code_snippet_map[key] = content
                except Exception as e:
                    logger.error(f"读取代码片段失败: {e}")
    return code_snippet_map


def process_model(path: Path, code_snippet_map: dict, before: str, after: str) -> CustomModel | None:
    try:
        with open(path, 'r') as f:
            data = yaml.load(f)

        # 替换代码片段
        instructions = data.get('customInstructions', '')
        for key, value in code_snippet_map.items():
            instructions = instructions.replace(f"{{{key}}}", value)

        # 合并模板
        data['customInstructions'] = f"{before}\n\n{instructions}\n\n{after}"
        data['source'] = 'global'
        # data['groups'] = ["read", "edit", "command", "browser", "mcp"]

        # 验证逻辑
        required_fields = ['slug', 'name', 'roleDefinition', 'customInstructions', 'whenToUse', 'description', 'groups']
        if any(field not in data for field in required_fields):
            logger.error("缺少必要字段")
            return None

        return CustomModel(data)

    except Exception as e:
        logger.error(f"处理模型失败: {e}")
        return None


def write_output(models: list, output_path: Path):
    try:
        with open(output_path, 'w') as f:
            yaml.dump({"customModes": [m.data for m in models]}, f)
        logger.info(f"生成成功: {output_path}")
    except Exception as e:
        logger.error(f"写入文件失败: {e}")


def run():
    before_path = Path("models_hook/before.md")
    after_path = Path("models_hook/after.md")

    try:
        with open(before_path, 'r') as f:
            before = f.read()
        with open(after_path, 'r') as f:
            after = f.read()
    except Exception as e:
        logger.error(f"读取嵌入文件失败: {e}")
        return

    code_snippet_map = load_code_snippets(Path("code_snippet"))
    model_paths = list(Path(root) / file for root, _, files in os.walk("custom_models") for file in files if file.endswith(".yaml"))
    total = len(model_paths)

    models = []

    with Progress() as progress:
        task = progress.add_task("[green]Processing models...", total=total)
        for path in model_paths:
            # 跳过 researcher 文件
            # if "researcher" in str(path):
            #     logger.info(f"跳过文件: {path}")
            #     progress.advance(task)
            #     continue

            logger.info(f"处理文件: {path}")
            model = process_model(path, code_snippet_map, before, after)
            if model:
                models.append(model)
            progress.advance(task)

    def sort_key(model):
        if model.slug == "orchestrator":
            return (0, model.slug)
        return (1, model.slug)

    models.sort(key=sort_key)
    write_output(models, Path("custom_models.yaml"))


if __name__ == "__main__":
    run()