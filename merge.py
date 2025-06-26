import logging
import os
from pathlib import Path

from rich.logging import RichHandler  # 新增rich日志支持
from rich.progress import Progress  # 新增进度条支持
from ruamel.yaml import YAML

# 配置日志（使用rich日志处理器）
logging.basicConfig(
	level=logging.INFO,
	handlers=[RichHandler(
		show_time=False,
	)],
	format="%(message)s"  # 修改: 移除时间展示，仅保留消息内容
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


def main():
	# 读取嵌入文件（需调整路径）
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

	# 收集代码片段
	code_snippet_map = {}
	for root, _, files in os.walk("code_snippet"):
		for file in files:
			if file.endswith(".md"):
				path = Path(root) / file
				key = path.stem
				try:
					with open(path, 'r') as f:
						content = f.read()
						if not content.endswith('\n'):
							content += '\n'
						code_snippet_map[key] = content
				except Exception as e:
					logger.error(f"读取代码片段失败: {e}")
					continue

	# 处理自定义模型
	models = []
	# 收集所有模型文件路径
	model_files = []
	for root, _, files in os.walk("custom_models"):
		for file in files:
			if file.endswith(".yaml"):
				model_files.append(Path(root) / file)
	total = len(model_files)

	# 创建进度条
	with Progress() as progress:
		task = progress.add_task("[green]Processing models...", total=total)

		for path in model_files:
			logger.info(f"处理文件: {path}")

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
				data['groups'] = ["read", "edit", "command", "browser", "mcp"]

				# 验证逻辑
				required_fields = ['slug', 'name', 'roleDefinition', 'customInstructions']
				if any(field not in data for field in required_fields):
					logger.error("缺少必要字段")
					continue

				models.append(CustomModel(data))

			except Exception as e:
				logger.error(f"处理模型失败: {e}")
				continue

			progress.advance(task)  # 更新进度条

	# 排序逻辑
	def sort_key(model):
		if model.slug == "brain":
			return (0, model.slug)
		return (1, model.slug)

	models.sort(key=sort_key)

	# 写入输出文件
	output_path = Path("custom_models.yaml")
	try:
		with open(output_path, 'w') as f:
			yaml.dump(
				{"customModes": [m.data for m in models]},
				f,
			)
		logger.info(f"生成成功: {output_path}")
	except Exception as e:
		logger.error(f"写入文件失败: {e}")


if __name__ == "__main__":
	main()