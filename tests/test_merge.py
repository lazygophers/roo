"""
测试 merge.py 模块的单元测试
"""

import pytest
from pathlib import Path
from unittest.mock import mock_open, patch, MagicMock
import tempfile
import os

from merge import CustomModel, process_model, write_output, run


class TestCustomModel:
    """测试 CustomModel 类"""
    
    def test_init_with_data(self):
        """测试使用数据初始化 CustomModel"""
        test_data = {'slug': 'test-slug', 'name': 'Test Model'}
        model = CustomModel(test_data)
        assert model.data == test_data
    
    def test_slug_property(self):
        """测试 slug 属性获取"""
        # 测试有 slug 的情况
        data_with_slug = {'slug': 'test-slug'}
        model = CustomModel(data_with_slug)
        assert model.slug == 'test-slug'
        
        # 测试没有 slug 的情况
        data_without_slug = {'name': 'Test Model'}
        model = CustomModel(data_without_slug)
        assert model.slug is None
    
    def test_source_property(self):
        """测试 source 属性获取和设置"""
        # 测试默认值
        data = {'slug': 'test'}
        model = CustomModel(data)
        assert model.source == 'global'
        
        # 测试设置值
        model.source = 'custom'
        assert model.source == 'custom'
        assert model.data['source'] == 'custom'


class TestProcessModel:
    """测试 process_model 函数"""
    
    @pytest.fixture
    def sample_yaml_content(self):
        """示例 YAML 内容"""
        return """
slug: test-model
name: Test Model
roleDefinition: Test role
customInstructions: |
  This is a test instruction
whenToUse: When needed
description: A test model
groups: ["read", "edit"]
"""
    
    @pytest.fixture
    def sample_yaml_file(self, sample_yaml_content):
        """创建临时 YAML 文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(sample_yaml_content)
            f.flush()
            yield Path(f.name)
        os.unlink(f.name)
    
    @pytest.fixture
    def before_content(self):
        """before.md 内容"""
        return "Global before content"
    
    @pytest.fixture
    def after_content(self):
        """after.md 内容"""
        return "Global after content"
    
    def test_process_model_success(self, sample_yaml_file, before_content, after_content):
        """测试成功处理模型文件"""
        result = process_model(sample_yaml_file, before_content, after_content)
        
        assert result is not None
        assert isinstance(result, CustomModel)
        assert result.slug == 'test-model'
        assert result.source == 'global'
        
        # 验证 customInstructions 被正确合并
        expected_instructions = f"{before_content}\n\n---\n\nThis is a test instruction\n\n\n---\n\n{after_content}"
        assert result.data['customInstructions'] == expected_instructions
    
    def test_process_model_missing_required_fields(self, sample_yaml_file, before_content, after_content):
        """测试缺少必需字段的情况"""
        # 修改文件内容，缺少必需字段
        with open(sample_yaml_file, 'w') as f:
            f.write("slug: test\nname: Test")  # 缺少 roleDefinition 等字段
        
        result = process_model(sample_yaml_file, before_content, after_content)
        assert result is None
    
    def test_process_model_file_not_found(self, before_content, after_content):
        """测试文件不存在的情况"""
        non_existent_path = Path("non_existent.yaml")
        result = process_model(non_existent_path, before_content, after_content)
        assert result is None
    
    def test_process_model_empty_custom_instructions(self, sample_yaml_file, before_content, after_content):
        """测试空 customInstructions 的情况"""
        # 修改文件内容，customInstructions 为空
        with open(sample_yaml_file, 'w') as f:
            f.write("""
slug: test-model
name: Test Model
roleDefinition: Test role
customInstructions: ''
whenToUse: When needed
description: A test model
groups: ["read", "edit"]
""")
        
        result = process_model(sample_yaml_file, before_content, after_content)
        assert result is not None
        
        # 验证即使 instructions 为空，也能正确合并
        expected_instructions = f"{before_content}\n\n---\n\n\n\n---\n\n{after_content}"
        assert result.data['customInstructions'] == expected_instructions


class TestWriteOutput:
    """测试 write_output 函数"""
    
    @pytest.fixture
    def sample_models(self):
        """创建示例模型列表"""
        model1 = CustomModel({
            'slug': 'model1',
            'name': 'Model 1',
            'roleDefinition': 'Role 1',
            'customInstructions': 'Instructions 1',
            'whenToUse': 'When 1',
            'description': 'Description 1',
            'groups': ['read'],
            'source': 'global'
        })
        model2 = CustomModel({
            'slug': 'model2',
            'name': 'Model 2',
            'roleDefinition': 'Role 2',
            'customInstructions': 'Instructions 2',
            'whenToUse': 'When 2',
            'description': 'Description 2',
            'groups': ['edit'],
            'source': 'global'
        })
        return [model1, model2]
    
    def test_write_output_success(self, sample_models):
        """测试成功写入输出文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.yaml"
            
            write_output(sample_models, output_path)
            
            # 验证文件被创建
            assert output_path.exists()
            
            # 验证文件内容
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert 'customModes:' in content
                assert 'model1' in content
                assert 'model2' in content
    
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    @patch('merge.logger')
    def test_write_output_error(self, mock_logger, sample_models):
        """测试写入文件失败的情况"""
        output_path = Path("output.yaml")
        write_output(sample_models, output_path)
        
        # 验证错误被记录
        mock_logger.error.assert_called_once()
        assert "Permission denied" in mock_logger.error.call_args[0][0]


class TestRun:
    """测试 run 函数"""
    
    @pytest.fixture
    def mock_files(self):
        """模拟文件结构"""
        # 创建临时目录结构
        temp_dir = tempfile.mkdtemp()
        resources_dir = Path(temp_dir) / "resources"
        hooks_dir = resources_dir / "hooks"
        models_dir = resources_dir / "models"
        
        hooks_dir.mkdir(parents=True)
        models_dir.mkdir(parents=True)
        
        # 创建 before.md 和 after.md
        (hooks_dir / "before.md").write_text("Before content")
        (hooks_dir / "after.md").write_text("After content")
        
        # 创建示例模型文件
        model_content = """
slug: test-model
name: Test Model
roleDefinition: Test role
customInstructions: Test instructions
whenToUse: When needed
description: Test description
groups: ["read", "edit"]
"""
        (models_dir / "model1.yaml").write_text(model_content)
        (models_dir / "model2.yaml").write_text(model_content.replace('test-model', 'orchestrator'))
        
        # 切换到临时目录
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        yield {
            'resources_dir': resources_dir,
            'hooks_dir': hooks_dir,
            'models_dir': models_dir,
            'temp_dir': temp_dir
        }
        
        # 恢复原始目录
        os.chdir(original_cwd)
        # 清理临时目录
        import shutil
        shutil.rmtree(temp_dir)
    
    @patch('merge.Progress')
    @patch('merge.logger')
    def test_run_success(self, mock_logger, mock_progress, mock_files):
        """测试成功运行主函数"""
        # 设置 mock
        mock_progress_instance = MagicMock()
        mock_progress.return_value.__enter__.return_value = mock_progress_instance
        mock_progress_instance.add_task = MagicMock()
        mock_progress_instance.advance = MagicMock()
        
        # 运行函数
        with patch('merge.write_output') as mock_write:
            run()
        
        # 验证进度条被创建
        mock_progress_instance.add_task.assert_called_once()
        
        # 验证 write_output 被调用
        mock_write.assert_called_once()
        
        # 验证输出文件路径
        output_path = mock_write.call_args[0][1]
        assert output_path == Path("custom_models.yaml")
    
    @patch('merge.logger')
    def test_run_no_models_found(self, mock_logger, mock_files):
        """测试没有找到模型文件的情况"""
        # 清空模型目录
        for model_file in mock_files['models_dir'].glob("*.yaml"):
            model_file.unlink()
        
        run()
        
        # 验证警告被记录
        mock_logger.warning.assert_called_once()
        assert "未找到任何 .yaml 文件" in mock_logger.warning.call_args[0][0]
    
    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    @patch('merge.logger')
    def test_run_missing_hook_files(self, mock_logger, mock_open):
        """测试缺少 hook 文件的情况"""
        run()
        
        # 验证错误被记录
        mock_logger.error.assert_called_once()
        assert "读取 before/after 嵌入文件失败" in mock_logger.error.call_args[0][0]


class TestEdgeCases:
    """测试边界情况和错误处理"""
    
    def test_custom_model_with_none_data(self):
        """测试 CustomModel 使用 None 数据"""
        model = CustomModel(None)
        assert model.data is None
        assert model.slug is None
        assert model.source == 'global'
    
    def test_custom_model_empty_data(self):
        """测试 CustomModel 使用空数据"""
        model = CustomModel({})
        assert model.data == {}
        assert model.slug is None
        assert model.source == 'global'
    
    @patch('merge.yaml.load', side_effect=Exception("YAML parsing error"))
    @patch('merge.logger')
    def test_process_model_yaml_error(self, mock_logger, mock_yaml_load):
        """测试 YAML 解析错误"""
        test_path = Path("test.yaml")
        result = process_model(test_path, "before", "after")
        
        assert result is None
        mock_logger.error.assert_called_once()
        assert "处理模型文件失败" in mock_logger.error.call_args[0][0]
    
    def test_write_output_empty_models(self):
        """测试写入空模型列表"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "output.yaml"
            write_output([], output_path)
            
            assert output_path.exists()
            with open(output_path, 'r') as f:
                content = f.read()
                assert 'customModes: []' in content
    
    def test_sort_key_orchestrator_first(self):
        """测试排序函数确保 orchestrator 在前"""
        models = [
            CustomModel({'slug': 'model1'}),
            CustomModel({'slug': 'orchestrator'}),
            CustomModel({'slug': 'model2'}),
            CustomModel({'slug': 'model3'}),
        ]
        
        # 模拟排序函数
        def sort_key(model):
            if model.slug == "orchestrator":
                return (0, model.slug)
            return (1, model.slug)
        
        sorted_models = sorted(models, key=sort_key)
        assert sorted_models[0].slug == 'orchestrator'
        assert all(m.slug != 'orchestrator' for m in sorted_models[1:])