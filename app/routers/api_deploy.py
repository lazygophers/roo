from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import yaml
import os
import shutil
import logging
from pathlib import Path

# 自定义 YAML 表示器，用于多行字符串
class CustomDumper(yaml.SafeDumper):
    def represent_str(self, data):
        # 如果字符串包含换行符，使用字面量块标量（|）
        if '\n' in data:
            return self.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return self.represent_scalar('tag:yaml.org,2002:str', data)

# 注册自定义表示器
CustomDumper.add_representer(str, CustomDumper.represent_str)
# BaseResponse不存在，直接使用内置响应模型
from app.core.database_service import get_database_service
from app.core.secure_logging import sanitize_for_log

logger = logging.getLogger(__name__)
router = APIRouter()

class DeployTarget(BaseModel):
    """部署目标配置"""
    name: str
    path: str
    enabled: bool = True
    description: str = ""

class DeployRequest(BaseModel):
    """部署请求数据结构"""
    selected_models: List[str]  # 选中的模型slug列表
    selected_commands: List[str]  # 选中的指令路径列表  
    selected_rules: List[str]  # 选中的规则路径列表
    model_rule_bindings: List[Dict[str, Any]]  # 模式-规则绑定关系
    selected_role: Optional[str] = None  # 选中的角色
    deploy_targets: List[str]  # 部署目标列表：roo, roo-nightly, kilo等

class DeployResponse(BaseModel):
    """部署响应数据结构"""
    success: bool
    message: str
    deployed_files: List[str] = []
    errors: List[str] = []

class CleanupRequest(BaseModel):
    """清空请求数据结构"""
    cleanup_type: str  # "models" 或 "directories"
    deploy_targets: List[str]  # 部署目标列表：roo, roo-nightly, kilo等

class CleanupResponse(BaseModel):
    """清空响应数据结构"""
    success: bool
    message: str
    cleaned_items: List[str] = []
    errors: List[str] = []

import platform

def get_platform_specific_path(extension_id: str) -> str:
    """根据操作系统返回正确的VS Code扩展配置路径"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        return f"~/Library/Application Support/Code/User/globalStorage/{extension_id}/settings/custom_modes.yaml"
    elif system == "Windows":
        return f"~/AppData/Roaming/Code/User/globalStorage/{extension_id}/settings/custom_modes.yaml"
    elif system == "Linux":
        return f"~/.config/Code/User/globalStorage/{extension_id}/settings/custom_modes.yaml"
    else:
        # 默认返回 Linux 路径
        return f"~/.config/Code/User/globalStorage/{extension_id}/settings/custom_modes.yaml"

# 预定义的部署目标（动态生成路径）
def get_deploy_targets():
    """动态生成基于当前操作系统的部署目标"""
    return {
        "roo": {
            "name": "Roo Cline",
            "path": get_platform_specific_path("rooveterinaryinc.roo-cline"),
            "description": "Roo Cline 扩展"
        },
        "roo-nightly": {
            "name": "Roo Nightly", 
            "path": get_platform_specific_path("rooveterinaryinc.roo-code-nightly"),
            "description": "Roo Nightly 版本"
        },
        "kilo": {
            "name": "Kilo Code",
            "path": get_platform_specific_path("kilocode.kilo-code"), 
            "description": "Kilo Code 扩展"
        }
    }

# 使用函数获取部署目标
DEPLOY_TARGETS = get_deploy_targets()

# 命令文件部署目标映射
COMMAND_DEPLOY_PATHS = {
    "roo": "~/.roo/commands",
    "roo-nightly": "~/.roo/commands", 
    "kilo": "~/.kilocode/commands"
}

# 规则文件部署目标映射（用于角色文件）
RULES_DEPLOY_PATHS = {
    "roo": "~/.roo/rules",
    "roo-nightly": "~/.roo/rules",
    "kilo": "~/.kilocode/rules"
}

def load_yaml_file(file_path: str) -> Dict[str, Any]:
    """加载YAML文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logger.error(f"Error loading YAML file {sanitize_for_log(file_path)}: {sanitize_for_log(str(e))}")
        return {}

def load_markdown_file(file_path: str) -> str:
    """加载Markdown文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading markdown file {sanitize_for_log(file_path)}: {sanitize_for_log(str(e))}")
        return ""

def load_hooks() -> tuple[str, str]:
    """加载before和after钩子内容"""
    resources_dir = Path(__file__).parent.parent.parent / "resources"
    hooks_dir = resources_dir / "hooks"
    
    before_content = ""
    after_content = ""
    
    before_file = hooks_dir / "before.md"
    if before_file.exists():
        before_content = load_markdown_file(str(before_file))
        # 移除YAML frontmatter
        if before_content.startswith('---'):
            parts = before_content.split('---', 2)
            if len(parts) >= 3:
                before_content = parts[2].strip()
    
    after_file = hooks_dir / "after.md"  
    if after_file.exists():
        after_content = load_markdown_file(str(after_file))
        # 移除YAML frontmatter
        if after_content.startswith('---'):
            parts = after_content.split('---', 2)
            if len(parts) >= 3:
                after_content = parts[2].strip()
                
    return before_content, after_content

def generate_custom_modes_yaml(
    selected_models: List[str],
    selected_commands: List[str], 
    selected_rules: List[str],
    model_rule_bindings: List[Dict[str, Any]],
    selected_role: Optional[str] = None
) -> Dict[str, Any]:
    """生成custom_modes.yaml格式的数据"""
    
    resources_dir = Path(__file__).parent.parent.parent / "resources"
    models_dir = resources_dir / "models"
    
    # 加载hooks
    before_content, after_content = load_hooks()
    
    custom_modes = []
    
    for model_slug in selected_models:
        # 查找模型文件
        model_file = None
        
        # 首先检查直接的yaml文件名匹配
        yaml_file = models_dir / f"{model_slug}.yaml"
        if yaml_file.exists():
            model_file = yaml_file
        else:
            # 检查目录中的yaml文件
            model_dir = models_dir / model_slug
            if model_dir.is_dir():
                for yaml_file in model_dir.glob("*.yaml"):
                    model_file = yaml_file
                    break
            
            # 如果还没找到，递归搜索所有yaml文件寻找匹配的slug
            if not model_file:
                for yaml_file in models_dir.rglob("*.yaml"):
                    try:
                        temp_data = load_yaml_file(str(yaml_file))
                        if temp_data.get('slug') == model_slug:
                            model_file = yaml_file
                            break
                    except Exception:
                        continue
        
        if not model_file:
            logger.warning(f"Model file not found for slug: {sanitize_for_log(model_slug)}")
            continue
            
        # 加载模型数据
        model_data = load_yaml_file(str(model_file))
        if not model_data:
            continue
            
        # 构建customInstructions
        custom_instructions_parts = []
        
        # 1. 添加before hook到最前面
        if before_content:
            custom_instructions_parts.append(before_content)
        
        # 2. 添加模式关联的规则
        model_bindings = [b for b in model_rule_bindings if b.get('modelId') == model_slug]
        for binding in model_bindings:
            for rule_path in binding.get('selectedRuleIds', []):
                if os.path.exists(rule_path):
                    rule_content = load_markdown_file(rule_path)
                    if rule_content:
                        # 移除YAML frontmatter
                        if rule_content.startswith('---'):
                            parts = rule_content.split('---', 2)
                            if len(parts) >= 3:
                                rule_content = parts[2].strip()
                        custom_instructions_parts.append(rule_content)
        
        # 3. 添加通用选中的规则
        for rule_path in selected_rules:
            if os.path.exists(rule_path):
                rule_content = load_markdown_file(rule_path) 
                if rule_content:
                    # 移除YAML frontmatter
                    if rule_content.startswith('---'):
                        parts = rule_content.split('---', 2)
                        if len(parts) >= 3:
                            rule_content = parts[2].strip()
                    custom_instructions_parts.append(rule_content)
        
        # 4. 添加原有的customInstructions
        if model_data.get('customInstructions'):
            custom_instructions_parts.append(model_data['customInstructions'])
            
        # 5. 添加after hook到最后
        if after_content:
            custom_instructions_parts.append(after_content)
        
        # 拼接所有内容
        final_custom_instructions = '\n\n'.join(filter(None, custom_instructions_parts))
        
        # 构建模式数据
        mode_data = {
            'slug': model_data.get('slug', model_slug),
            'name': model_data.get('name', model_slug),
            'roleDefinition': model_data.get('roleDefinition', ''),
            'whenToUse': model_data.get('whenToUse', ''), 
            'description': model_data.get('description', ''),
            'groups': model_data.get('groups', []),
            'customInstructions': final_custom_instructions
        }
        
        custom_modes.append(mode_data)
    
    return {'customModes': custom_modes}

@router.get(
    "/targets",
    response_model=Dict[str, DeployTarget],
    summary="获取部署目标列表", 
    description="获取所有可用的部署目标配置"
)
async def get_deploy_targets():
    """获取部署目标列表"""
    targets = {}
    for key, config in DEPLOY_TARGETS.items():
        targets[key] = DeployTarget(
            name=config["name"],
            path=config["path"],
            description=config["description"],
            enabled=True
        )
    return targets

@router.post(
    "/generate",
    response_model=Dict[str, Any],
    summary="生成custom_modes.yaml",
    description="根据用户选择生成custom_modes.yaml格式的配置"
)
async def generate_custom_modes(request: DeployRequest):
    """生成custom_modes.yaml配置"""
    try:
        yaml_data = generate_custom_modes_yaml(
            request.selected_models,
            request.selected_commands,
            request.selected_rules, 
            request.model_rule_bindings,
            request.selected_role
        )
        
        return {
            "success": True,
            "message": "Custom modes YAML generated successfully",
            "data": yaml_data
        }
        
    except Exception as e:
        logger.error(f"Error generating custom modes YAML: {sanitize_for_log(str(e))}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate custom modes YAML: {str(e)}"
        )

@router.post(
    "/deploy", 
    response_model=DeployResponse,
    summary="部署配置文件",
    description="生成并部署custom_modes.yaml到指定目标"
)
async def deploy_custom_modes(request: DeployRequest):
    """部署custom_modes.yaml到指定目标"""
    deployed_files = []
    errors = []
    
    try:
        # 1. 生成YAML数据
        yaml_data = generate_custom_modes_yaml(
            request.selected_models,
            request.selected_commands, 
            request.selected_rules,
            request.model_rule_bindings,
            request.selected_role
        )
        
        # 2. 生成YAML字符串（使用自定义dumper支持多行字符串）
        yaml_content = yaml.dump(yaml_data, Dumper=CustomDumper, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        # 3. 写入临时文件
        temp_yaml_file = Path(__file__).parent.parent.parent / "custom_modes.yaml"
        with open(temp_yaml_file, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        # 4. 部署到各个目标
        for target_key in request.deploy_targets:
            if target_key not in DEPLOY_TARGETS:
                errors.append(f"Unknown deploy target: {target_key}")
                continue
                
            target_config = DEPLOY_TARGETS[target_key]
            target_path = os.path.expanduser(target_config["path"])
            
            try:
                # 确保目标目录存在
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                
                # 复制自定义模式YAML文件
                shutil.copy2(str(temp_yaml_file), target_path)
                deployed_files.append(target_path)
                
                logger.info(f"Successfully deployed custom modes to {sanitize_for_log(target_config['name'])}: {sanitize_for_log(str(target_path))}")
                
                # 5. 部署选中的命令文件
                if request.selected_commands and target_key in COMMAND_DEPLOY_PATHS:
                    command_target_dir = os.path.expanduser(COMMAND_DEPLOY_PATHS[target_key])
                    os.makedirs(command_target_dir, exist_ok=True)
                    
                    for command_path in request.selected_commands:
                        if os.path.exists(command_path):
                            command_filename = os.path.basename(command_path)
                            command_target_path = os.path.join(command_target_dir, command_filename)
                            
                            try:
                                shutil.copy2(command_path, command_target_path)
                                deployed_files.append(command_target_path)
                                logger.info(f"Successfully deployed command to {sanitize_for_log(target_config['name'])}: {sanitize_for_log(str(command_target_path))}")
                            except Exception as e:
                                error_msg = f"Failed to deploy command {command_filename} to {target_config['name']}: {str(e)}"
                                errors.append(error_msg)
                                logger.error(error_msg)
                        else:
                            sanitized_command_path = command_path.replace('\r', '').replace('\n', '')
                            error_msg = f"Command file not found: {sanitized_command_path}"
                            errors.append(error_msg)
                            logger.warning(error_msg)

                # 6. 部署选中的角色文件
                if request.selected_role and target_key in RULES_DEPLOY_PATHS:
                    rules_target_dir = os.path.expanduser(RULES_DEPLOY_PATHS[target_key])
                    os.makedirs(rules_target_dir, exist_ok=True)
                    
                    # 构建角色文件路径
                    role_file_path = f"resources/roles/{request.selected_role}.md"
                    
                    if os.path.exists(role_file_path):
                        role_target_path = os.path.join(rules_target_dir, "role.md")
                        
                        try:
                            shutil.copy2(role_file_path, role_target_path)
                            deployed_files.append(role_target_path)
                            logger.info(f"Successfully deployed role to {sanitize_for_log(target_config['name'])}: {sanitize_for_log(str(role_target_path))}")
                        except Exception as e:
                            error_msg = f"Failed to deploy role {request.selected_role} to {target_config['name']}: {str(e)}"
                            errors.append(error_msg)
                            logger.error(error_msg)
                    else:
                        error_msg = f"Role file not found: {role_file_path}"
                        errors.append(error_msg)
                        logger.warning(error_msg)
                
            except Exception as e:
                error_msg = f"Failed to deploy to {target_config['name']}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        # 7. 清理临时文件（可选，保留用于调试）
        # temp_yaml_file.unlink(missing_ok=True)
        
        success = len(deployed_files) > 0
        message = f"Deployment completed. Deployed to {len(deployed_files)} targets."
        if errors:
            message += f" {len(errors)} errors occurred."
            
        return DeployResponse(
            success=success,
            message=message,
            deployed_files=deployed_files,
            errors=errors
        )
        
    except Exception as e:
        logger.error(f"Error during deployment: {sanitize_for_log(str(e))}")
        return DeployResponse(
            success=False,
            message=f"Deployment failed: {str(e)}",
            deployed_files=deployed_files,
            errors=errors + [str(e)]
        )

@router.post(
    "/cleanup",
    response_model=CleanupResponse,
    summary="清空配置",
    description="清空指定目标的模型配置文件或目录"
)
async def cleanup_configurations(request: CleanupRequest):
    """清空配置文件或目录"""
    cleaned_items = []
    errors = []
    
    try:
        for target_key in request.deploy_targets:
            if target_key not in DEPLOY_TARGETS:
                errors.append(f"Unknown deploy target: {target_key}")
                continue
                
            target_config = DEPLOY_TARGETS[target_key]
            
            if request.cleanup_type == "models":
                # 清空模型配置文件
                target_path = os.path.expanduser(target_config["path"])
                try:
                    if os.path.exists(target_path):
                        os.remove(target_path)
                        cleaned_items.append(target_path)
                        logger.info(f"Successfully removed model config from {sanitize_for_log(target_config['name'])}: {sanitize_for_log(str(target_path))}")
                    else:
                        logger.info(f"Model config file not found at {sanitize_for_log(str(target_path))}")
                except Exception as e:
                    error_msg = f"Failed to remove model config from {target_config['name']}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    
            elif request.cleanup_type == "directories":
                # 清空整个目录结构
                if target_key in COMMAND_DEPLOY_PATHS:
                    # 清空命令目录
                    command_dir = os.path.expanduser(COMMAND_DEPLOY_PATHS[target_key])
                    try:
                        if os.path.exists(command_dir):
                            for file in os.listdir(command_dir):
                                file_path = os.path.join(command_dir, file)
                                if os.path.isfile(file_path):
                                    os.remove(file_path)
                                    cleaned_items.append(file_path)
                            logger.info(f"Successfully cleaned command directory for {sanitize_for_log(target_config['name'])}: {sanitize_for_log(str(command_dir))}")
                        else:
                            logger.info(f"Command directory not found at {sanitize_for_log(str(command_dir))}")
                    except Exception as e:
                        error_msg = f"Failed to clean command directory for {target_config['name']}: {str(e)}"
                        errors.append(error_msg)
                        logger.error(error_msg)
                
                # 清空规则目录中的角色文件
                if target_key in RULES_DEPLOY_PATHS:
                    rules_dir = os.path.expanduser(RULES_DEPLOY_PATHS[target_key])
                    role_file_path = os.path.join(rules_dir, "role.md")
                    try:
                        if os.path.exists(role_file_path):
                            os.remove(role_file_path)
                            cleaned_items.append(role_file_path)
                            logger.info(f"Successfully cleaned role file for {sanitize_for_log(target_config['name'])}: {sanitize_for_log(str(role_file_path))}")
                        else:
                            logger.info(f"Role file not found at {sanitize_for_log(str(role_file_path))}")
                    except Exception as e:
                        error_msg = f"Failed to clean role file for {target_config['name']}: {str(e)}"
                        errors.append(error_msg)
                        logger.error(error_msg)
                
                # 同时清空模型配置文件
                target_path = os.path.expanduser(target_config["path"])
                try:
                    if os.path.exists(target_path):
                        os.remove(target_path)
                        cleaned_items.append(target_path)
                        logger.info(f"Successfully removed model config from {sanitize_for_log(target_config['name'])}: {sanitize_for_log(str(target_path))}")
                except Exception as e:
                    error_msg = f"Failed to remove model config from {target_config['name']}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    
            else:
                errors.append(f"Unknown cleanup type: {request.cleanup_type}")
        
        success = len(cleaned_items) > 0 or len(errors) == 0
        message = f"Cleanup completed. Cleaned {len(cleaned_items)} items."
        if errors:
            message += f" {len(errors)} errors occurred."
            
        return CleanupResponse(
            success=success,
            message=message,
            cleaned_items=cleaned_items,
            errors=errors
        )
        
    except Exception as e:
        logger.error(f"Error during cleanup: {sanitize_for_log(str(e))}")
        return CleanupResponse(
            success=False,
            message=f"Cleanup failed: {str(e)}",
            cleaned_items=cleaned_items,
            errors=errors + [str(e)]
        )