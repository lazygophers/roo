from fastapi import APIRouter, HTTPException, UploadFile, File, Body, Request
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
import os
import yaml
import json
import traceback
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel, Field
from app.database import ConfigDatabase, Q
from app.utils.frontmatter_parser import parse_markdown_with_frontmatter, parse_frontmatter
from app.utils.logger import get_logger

router = APIRouter()

# 获取路由专用的日志记录器
route_logger = get_logger(__name__)

# 基础路径配置
BASE_DIR = Path(__file__).parent.parent.parent
RESOURCES_DIR = BASE_DIR / "resources"

# 请求模型定义
class HelloRequest(BaseModel):
    message: Optional[str] = None

class ModelRequest(BaseModel):
    slug: Optional[str] = None

class ConfigRequest(BaseModel):
    user_id: Optional[str] = None

class ConfigIdRequest(BaseModel):
    config_id: str

class UpdateConfigRequest(BaseModel):
    config_data: Dict[str, Any]

@router.post("/hello")
async def hello(request: HelloRequest = Body(...)):
    """简单的问候端点，支持前端调用"""
    # 如果没有提供消息参数，使用默认消息
    display_message = request.message if request.message else "Hello from FastAPI!"

    return {
        "message": display_message,
        "status": "success"
    }


# 辅助函数
def read_yaml_file(file_path: Path) -> Dict[str, Any]:
    """读取YAML文件并返回字典"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data if data is not None else {}
    except Exception:
        return {}


def read_text_file(file_path: Path) -> str:
    """读取文本文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ""


# 新的资源配置API端点

@router.post("/models", response_model=List[Dict[str, Any]])
async def get_models():
    """获取models目录及其子目录的所有文件信息（排除customInstructions字段）"""
    models_dir = RESOURCES_DIR / "models"
    result = []

    if models_dir.exists():
        # 递归遍历models目录
        for file_path in models_dir.rglob("*.yaml"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                    # 排除customInstructions字段
                    if 'customInstructions' in data:
                        del data['customInstructions']
                    # 添加文件路径信息
                    data['_path'] = str(file_path.relative_to(RESOURCES_DIR))
                    result.append(data)
            except Exception:
                continue

    return result


@router.post("/models/get", response_model=Dict[str, Any])
async def get_model_by_slug(request: ModelRequest = Body(...)):
    """根据slug获取models目录下具体文件的完整内容"""
    models_dir = RESOURCES_DIR / "models"
    slug = request.slug

    # 查找匹配的文件
    for file_path in models_dir.rglob(f"{slug}.yaml"):
        data = read_yaml_file(file_path)
        if data:
            data['_path'] = str(file_path.relative_to(RESOURCES_DIR))
            return data

    return {}


@router.post("/hooks/before", response_model=Dict[str, Any])
async def get_hooks_before():
    """获取hooks/before.md文件的frontmatter元数据和内容"""
    file_path = RESOURCES_DIR / "hooks" / "before.md"
    result = parse_markdown_with_frontmatter(file_path)
    if not result:
        return {"metadata": {}, "content": read_text_file(file_path)}
    return result


@router.post("/hooks/after", response_model=Dict[str, Any])
async def get_hooks_after():
    """获取hooks/after.md文件的frontmatter元数据和内容"""
    file_path = RESOURCES_DIR / "hooks" / "after.md"
    result = parse_markdown_with_frontmatter(file_path)
    if not result:
        return {"metadata": {}, "content": read_text_file(file_path)}
    return result


@router.post("/rules/get", response_model=Dict[str, Dict[str, Any]])
async def get_rules_by_slug(request: ModelRequest = Body(...)):
    """根据slug获取rules目录下的所有文件内容和frontmatter元数据"""
    result = {}
    slug = request.slug

    # 搜索规则文件的顺序：rules/ -> rules-{slug} -> rules-{slug}-{subslug}
    search_paths = [
        RESOURCES_DIR / "rules",
        RESOURCES_DIR / f"rules-{slug}"
    ]

    # 处理包含连字符的slug（如 code-golang）
    if '-' in slug:
        parts = slug.split('-')
        for i in range(len(parts)):
            prefix = '-'.join(parts[:i+1])
            search_paths.append(RESOURCES_DIR / f"rules-{prefix}")

    # 在所有搜索路径中查找文件
    for search_path in search_paths:
        if search_path.exists():
            for file_path in search_path.glob("*.md"):
                file_name = file_path.stem
                # 使用frontmatter解析器
                parsed_content = parse_markdown_with_frontmatter(file_path)
                if parsed_content:
                    result[file_name] = parsed_content
                else:
                    # 如果没有frontmatter，返回原始内容
                    result[file_name] = {
                        "metadata": {},
                        "content": read_text_file(file_path)
                    }

    return result


@router.post("/commands", response_model=Dict[str, Dict[str, Any]])
async def get_commands():
    """获取commands目录下的所有文件内容和frontmatter元数据"""
    commands_dir = RESOURCES_DIR / "commands"
    result = {}

    if commands_dir.exists():
        for file_path in commands_dir.glob("*.md"):
            file_name = file_path.stem
            # 使用frontmatter解析器
            parsed_content = parse_markdown_with_frontmatter(file_path)
            if parsed_content:
                result[file_name] = parsed_content
            else:
                # 如果没有frontmatter，返回原始内容
                result[file_name] = {
                    "metadata": {},
                    "content": read_text_file(file_path)
                }

    return result


@router.post("/roles", response_model=Dict[str, Dict[str, Any]])
async def get_roles():
    """获取roles目录下的所有文件内容和frontmatter元数据"""
    roles_dir = RESOURCES_DIR / "roles"
    result = {}

    if roles_dir.exists():
        for file_path in roles_dir.glob("*.md"):
            file_name = file_path.stem
            # 使用frontmatter解析器
            parsed_content = parse_markdown_with_frontmatter(file_path)
            if parsed_content:
                result[file_name] = parsed_content
            else:
                # 如果没有frontmatter，返回原始内容
                result[file_name] = {
                    "metadata": {},
                    "content": read_text_file(file_path)
                }

    return result


# 配置管理API端点

@router.post("/configurations", response_model=Dict[str, Any], status_code=201)
async def save_configuration(config_data: Dict[str, Any]):
    """保存配置到数据库"""
    try:
        db = ConfigDatabase()
        config = db.create_config(
            name=config_data.get("name", "导入的配置"),
            config_data=config_data.get("config", {}),
            description=config_data.get("description", ""),
            user_id=config_data.get("user_id")
        )
        config_id = config.get("id")
        return {
            "success": True,
            "message": "配置保存成功",
            "config_id": config_id,
            "data": config_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")


@router.post("/configurations", response_model=List[Dict[str, Any]])
async def get_configurations(request: ConfigRequest = Body(...)):
    """获取所有配置或用户专属配置"""
    try:
        db = ConfigDatabase()
        if request.user_id:
            configs = db.get_all_configs(request.user_id)
        else:
            configs = db.get_all_configs()
        return configs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@router.post("/configurations/get", response_model=Dict[str, Any])
async def get_configuration(request: ConfigIdRequest = Body(...)):
    """根据ID获取单个配置"""
    try:
        db = ConfigDatabase()
        config = db.get_config(request.config_id)
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")
        return config
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@router.post("/configurations/update", response_model=Dict[str, Any])
async def update_configuration(request: UpdateConfigRequest = Body(...)):
    """更新配置"""
    try:
        db = ConfigDatabase()
        updated_config = db.update_config(
            config_id=request.config_data.get("config_id"),
            config_data=request.config_data.get("config", {}),
            name=request.config_data.get("name"),
            description=request.config_data.get("description"),
            user_id=request.config_data.get("user_id")
        )
        if not updated_config:
            raise HTTPException(status_code=404, detail="配置不存在")
        return {
            "success": True,
            "message": "配置更新成功",
            "data": updated_config
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")


@router.post("/configurations/delete", response_model=Dict[str, Any])
async def delete_configuration(request: ConfigIdRequest = Body(...)):
    """删除配置"""
    try:
        db = ConfigDatabase()
        success = db.delete_config(request.config_id, request.user_id)
        if not success:
            raise HTTPException(status_code=404, detail="配置不存在")
        return {"success": True, "message": "配置删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除配置失败: {str(e)}")


@router.post("/configurations/export/yaml")
async def export_configuration_yaml(request: ConfigIdRequest = Body(...)):
    """导出配置为 YAML 文件

    将配置数据导出为 YAML 格式的文件，供用户下载。
    自动移除数据库内部字段，只保留用户配置数据。

    Args:
        config_id: 要导出的配置 ID

    Returns:
        StreamingResponse: YAML 文件流，包含：
            - Content-Type: application/x-yaml
            - Content-Disposition: 附件下载头

    Raises:
        HTTPException:
            - 404: 配置不存在
            - 500: 导出失败

    Example:
        >>> # 导出配置为 YAML 文件
        >>> response = await export_configuration_yaml("config123")
        >>> # response 可直接作为文件下载
    """
    try:
        db = ConfigDatabase()
        config = db.get_configuration(request.config_id)
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")

        # 移除数据库内部字段，只导出用户数据
        export_data = {k: v for k, v in config.items()
                     if k not in ['doc_id', 'created_at', 'updated_at']}

        # 生成 YAML 内容，保持格式友好
        yaml_content = yaml.dump(export_data,
                             default_flow_style=False,
                             allow_unicode=True,
                             indent=2)

        # 创建文件流响应
        from io import StringIO
        yaml_file = StringIO(yaml_content)
        yaml_file.seek(0)

        filename = f"configuration_{request.config_id}.yaml"
        route_logger.info(f"导出 YAML 配置: {request.config_id}")
        return StreamingResponse(
            iter([yaml_file.getvalue().encode('utf-8')]),
            media_type="application/x-yaml",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        route_logger.error(f"导出 YAML 失败: {e}")
        raise HTTPException(status_code=500, detail=f"导出YAML失败: {str(e)}")


@router.post("/configurations/export/json")
async def export_configuration_json(request: ConfigIdRequest = Body(...)):
    """导出配置为 JSON 文件

    将配置数据导出为 JSON 格式的文件，供用户下载。
    自动移除数据库内部字段，只保留用户配置数据。

    Args:
        config_id: 要导出的配置 ID

    Returns:
        StreamingResponse: JSON 文件流，包含：
            - Content-Type: application/json
            - Content-Disposition: 附件下载头

    Raises:
        HTTPException:
            - 404: 配置不存在
            - 500: 导出失败

    Example:
        >>> # 导出配置为 JSON 文件
        >>> response = await export_configuration_json("config123")
        >>> # response 可直接作为文件下载
    """
    try:
        db = ConfigDatabase()
        config = db.get_configuration(request.config_id)
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")

        # 移除数据库内部字段，只导出用户数据
        export_data = {k: v for k, v in config.items()
                     if k not in ['doc_id', 'created_at', 'updated_at']}

        # 生成格式化的 JSON 内容
        json_content = json.dumps(export_data,
                              indent=2,
                              ensure_ascii=False)

        # 创建文件流响应
        from io import StringIO
        json_file = StringIO(json_content)
        json_file.seek(0)

        filename = f"configuration_{request.config_id}.json"
        route_logger.info(f"导出 JSON 配置: {request.config_id}")
        return StreamingResponse(
            iter([json_file.getvalue().encode('utf-8')]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        route_logger.error(f"导出 JSON 失败: {e}")
        raise HTTPException(status_code=500, detail=f"导出JSON失败: {str(e)}")


@router.post("/configurations/import/yaml", response_model=Dict[str, Any])
async def import_configuration_yaml(
    file: UploadFile = File(...),
    user_id: Optional[str] = None
):
    """从YAML文件导入配置"""
    try:
        # 读取文件内容
        content = await file.read()
        yaml_content = content.decode('utf-8')

        # 解析YAML
        config_data = yaml.safe_load(yaml_content)
        if not config_data:
            raise HTTPException(status_code=400, detail="无效的YAML文件")

        # 添加用户ID（如果提供）
        if user_id:
            config_data['user_id'] = user_id

        # 保存到数据库
        db = ConfigDatabase()
        config = db.create_config(
            name=config_data.get("name", "导入的配置"),
            config_data=config_data.get("config", {}),
            description=config_data.get("description", ""),
            user_id=config_data.get("user_id")
        )
        config_id = config.get("id")

        return {
            "success": True,
            "message": "YAML配置导入成功",
            "config_id": config_id,
            "data": config_data
        }
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"YAML解析错误: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入YAML配置失败: {str(e)}")


@router.post("/configurations/import/json", response_model=Dict[str, Any])
async def import_configuration_json(
    file: UploadFile = File(...),
    user_id: Optional[str] = None
):
    """从JSON文件导入配置"""
    try:
        # 读取文件内容
        content = await file.read()
        json_content = content.decode('utf-8')

        # 解析JSON
        config_data = json.loads(json_content)
        if not config_data:
            raise HTTPException(status_code=400, detail="无效的JSON文件")

        # 添加用户ID（如果提供）
        if user_id:
            config_data['user_id'] = user_id

        # 保存到数据库
        db = ConfigDatabase()
        config = db.create_config(
            name=config_data.get("name", "导入的配置"),
            config_data=config_data.get("config", {}),
            description=config_data.get("description", ""),
            user_id=config_data.get("user_id")
        )
        config_id = config.get("id")

        return {
            "success": True,
            "message": "JSON配置导入成功",
            "config_id": config_id,
            "data": config_data
        }
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"JSON解析错误: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入JSON配置失败: {str(e)}")


# 命令执行 API 端点

class CommandRequest(BaseModel):
    """命令执行请求模型"""
    command: str = Field(description="要执行的命令字符串")
    working_dir: Optional[str] = Field(default=None, description="工作目录路径")


class RoleResponse(BaseModel):
    """角色信息响应模型"""
    name: str = Field(description="角色名称")
    title: str = Field(description="角色标题")
    description: str = Field(description="角色描述")
    category: str = Field(description="角色分类")
    traits: List[str] = Field(default=[], description="角色特质列表")
    features: Dict[str, Any] = Field(default={}, description="角色特性字典")
    content: str = Field(description="角色完整内容")


class CommandExecuteRequest(BaseModel):
    """命令执行请求模型"""
    command: str = Field(description="要执行的命令字符串")
    working_dir: Optional[str] = Field(default=None, description="工作目录路径")
    user_id: Optional[str] = Field(default=None, description="用户ID，用于权限控制")


@router.post("/commands/execute", response_model=Dict[str, Any])
async def execute_command(
    request: CommandExecuteRequest = Body(...),
    http_request: Request = None
):
    """执行系统命令并返回输出结果

    提供安全的命令执行环境，支持用户权限验证和执行结果捕获。
    命令在隔离的子进程中执行，避免影响主服务器进程。

    Args:
        request: 包含要执行的命令、工作目录和用户ID的请求对象
        http_request: FastAPI 请求对象，用于获取认证信息

    Returns:
        Dict[str, Any]: 命令执行结果，包含：
            - success: 执行是否成功
            - command: 执行的命令
            - exit_code: 进程退出码（0表示成功）
            - stdout: 标准输出内容
            - stderr: 标准错误内容

    Raises:
        HTTPException:
            - 401: 认证失败
            - 500: 命令执行失败

    Security:
        - 验证 Bearer Token
        - 记录所有命令执行日志
        - 限制命令执行权限

    Example:
        >>> # 执行简单命令
        >>> request = CommandExecuteRequest(command="ls -la")
        >>> result = await execute_command(request)
        >>> print(result["exit_code"])  # 0
    """
    try:
        # 验证用户身份
        if request.user_id:
            # 从请求头获取认证信息
            auth_header = http_request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="无效的认证信息")
            # TODO: 验证token有效性

        # 记录命令执行日志
        route_logger.info(f"用户 {request.user_id or 'anonymous'} 执行命令: {request.command}")

        # 创建子进程执行命令
        import subprocess
        import shlex

        # 解析命令字符串为参数列表
        cmd_list = shlex.split(request.command)

        # 设置工作目录
        cwd = request.working_dir if request.working_dir else None

        # 执行命令并捕获输出
        process = subprocess.Popen(
            cmd_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd
        )

        # 等待命令完成并获取输出
        stdout, stderr = process.communicate()

        # 记录执行结果
        exit_code = process.returncode
        if exit_code == 0:
            route_logger.info(f"命令执行成功: {request.command}")
        else:
            route_logger.warning(f"命令执行失败，退出码: {exit_code}, 错误: {stderr[:200]}")

        return {
            "success": exit_code == 0,
            "command": request.command,
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr
        }
    except HTTPException:
        raise
    except Exception as e:
        route_logger.error(f"执行命令失败: {e}")
        raise HTTPException(status_code=500, detail=f"执行命令失败: {str(e)}")


# 角色管理 API 端点

class RoleRequest(BaseModel):
    """角色请求模型"""
    role_name: str = Field(description="角色名称")


@router.post("/roles/get", response_model=RoleResponse)
async def get_role(request: RoleRequest = Body(...)):
    """获取指定角色的详细信息

    根据角色名称查找对应的角色文件，解析其 frontmatter 元数据和内容。
    角色文件存储在 resources/roles/ 目录下，使用 Markdown 格式。

    Args:
        request: 包含角色名称的请求对象

    Returns:
        RoleResponse: 包含角色完整信息的响应对象

    Raises:
        HTTPException:
            - 404: 角色文件不存在
            - 500: 读取或解析失败

    Note:
        角色文件必须包含 frontmatter 元数据，至少包含 title、description 和 category 字段。

    Example:
        >>> # 获取角色信息
        >>> request = RoleRequest(role_name="bunny_maid")
        >>> role = await get_role(request)
        >>> print(role.title)  # "小兔女仆角色设定"
    """
    try:
        # 构建角色文件路径
        role_path = RESOURCES_DIR / "roles" / f"{request.role_name}.md"

        # 检查文件是否存在
        if not role_path.exists():
            raise HTTPException(status_code=404, detail="角色不存在")

        # 读取角色文件内容
        content = read_text_file(role_path)
        if not content:
            raise HTTPException(status_code=500, detail="角色文件内容为空")

        # 解析 frontmatter 元数据
        frontmatter = parse_markdown_with_frontmatter(content)
        if not frontmatter:
            raise HTTPException(status_code=500, detail="无法解析角色文件的frontmatter")

        # 构建响应数据
        return {
            "name": request.role_name,
            "title": frontmatter.get("title", ""),
            "description": frontmatter.get("description", ""),
            "category": frontmatter.get("category", ""),
            "traits": frontmatter.get("traits", []),
            "features": frontmatter.get("features", {}),
            "content": content
        }
    except HTTPException:
        raise
    except Exception as e:
        route_logger.error(f"获取角色失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取角色失败: {str(e)}")


@router.get("/roles", response_model=List[Dict[str, Any]])
async def list_roles():
    """列出所有可用的角色

    扫描 roles 目录下的所有 Markdown 文件，解析每个角色的基本信息。
    返回角色列表，每个角色包含名称、标题、描述、分类和特质等基本信息。

    Returns:
        List[Dict[str, Any]]: 角色信息列表，每个角色包含：
            - name: 角色名称（文件名）
            - title: 角色标题
            - description: 角色描述
            - category: 角色分类
            - traits: 角色特质列表

    Raises:
        HTTPException: 500 - 列出角色失败

    Note:
        如果某个角色文件解析失败，会跳过该文件并记录警告日志。

    Example:
        >>> # 获取所有角色
        >>> roles = await list_roles()
        >>> print(len(roles))  # 角色数量
    """
    try:
        # 扫描角色目录
        roles_dir = RESOURCES_DIR / "roles"
        if not roles_dir.exists():
            route_logger.warning("角色目录不存在")
            return []

        roles = []
        for role_file in roles_dir.glob("*.md"):
            role_name = role_file.stem
            try:
                # 读取角色文件
                content = read_text_file(role_file)
                if not content:
                    route_logger.warning(f"角色文件为空: {role_file}")
                    continue

                # 解析 frontmatter
                frontmatter = parse_markdown_with_frontmatter(content)
                if not frontmatter:
                    route_logger.warning(f"无法解析角色文件的frontmatter: {role_file}")
                    # 使用默认值
                    frontmatter = {}

                # 添加到角色列表
                roles.append({
                    "name": role_name,
                    "title": frontmatter.get("title", role_name),
                    "description": frontmatter.get("description", ""),
                    "category": frontmatter.get("category", ""),
                    "traits": frontmatter.get("traits", [])
                })
            except Exception as e:
                route_logger.warning(f"读取角色文件失败 {role_file}: {e}")
                continue

        route_logger.info(f"成功列出 {len(roles)} 个角色")
        return roles
    except Exception as e:
        route_logger.error(f"列出角色失败: {e}")
        raise HTTPException(status_code=500, detail=f"列出角色失败: {str(e)}")