"""
YAML Frontmatter 解析工具模块

该模块提供了用于解析 Markdown 文件中 YAML frontmatter 的功能。
YAML frontmatter 是一种在 Markdown 文件顶部嵌入元数据的标准格式，
广泛用于静态站点生成器、文档系统和内容管理系统。

主要功能：
- 解析包含 YAML frontmatter 的 Markdown 文件
- 提取元数据和正文内容
- 验证 YAML 格式的正确性
- 提供便捷的工具函数进行文件操作

使用示例：
    >>> from app.utils.frontmatter_parser import FrontmatterParser
    >>> metadata, content = FrontmatterParser.parse_file(Path("example.md"))
    >>> print(f"标题: {metadata.get('title')}")
    >>> print(f"内容长度: {len(content)}")
"""
import re
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from app.utils.logger import utils_logger


class FrontmatterParser:
    """YAML Frontmatter 解析器
    
    这个类提供了完整的 YAML frontmatter 解析功能，支持从字符串或文件中
    提取元数据和内容。使用了预编译的正则表达式来提高解析效率。
    
    设计模式：
    - 使用类方法而不是实例方法，因为解析器是无状态的
    - 预编译正则表达式以提高性能
    - 优雅的错误处理，确保在解析失败时能够返回合理的默认值
    
    YAML frontmatter 格式示例：
        ---
        title: 文档标题
        author: 作者名
        date: 2024-01-01
        tags: [Python, 工具]
        ---
        
        这里是文档正文内容...
    """
    
    # Frontmatter 正则表达式模式
    # 解释：
    # ^---\s*\n  - 匹配开始分隔符 "---" 后跟换行
    # (.*?)       - 非贪婪匹配 frontmatter 内容（捕获组1）
    # \n---\s*\n  - 匹配结束分隔符 "---" 后跟换行
    # (.*)$      - 匹配剩余的所有内容（捕获组2）
    # re.DOTALL   - 使 . 匹配包括换行符在内的所有字符
    FRONTMATTER_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n(.*)$', re.DOTALL)
    
    @classmethod
    def parse(cls, content: str) -> Tuple[Dict[str, Any], str]:
        """解析包含 YAML frontmatter 的内容
        
        这是核心解析方法，使用预编译的正则表达式来提取和解析 frontmatter。
        方法设计考虑了各种边界情况和错误处理，确保在输入格式不正确时
        也能优雅地降级处理。
        
        Args:
            content: 包含 YAML frontmatter 的完整内容字符串
            
        Returns:
            Tuple[metadata, content]:
                - metadata: 解析出的元数据字典，如果没有 frontmatter 则为空字典
                - content: 剩余的正文内容，如果没有 frontmatter 则返回原内容
                
        Examples:
            >>> content = "---\\ntitle: 测试\\n---\\n正文内容\\n"
            >>> metadata, text = FrontmatterParser.parse(content)
            >>> print(metadata)  # {'title': '测试'}
            >>> print(text)      # '正文内容\\n'
            
        Note:
            - 使用 yaml.safe_load 而不是 yaml.load，避免潜在的安全风险
            - 如果 YAML 解析失败，会打印错误信息并返回空元数据
            - 空的 frontmatter（只有分隔符没有内容）会返回空元数据字典
        """
        # 使用预编译的正则表达式匹配内容
        match = cls.FRONTMATTER_PATTERN.match(content)
        
        if match:
            # 成功匹配到 frontmatter 格式
            frontmatter_yaml = match.group(1)  # 提取 YAML 部分
            remaining_content = match.group(2)  # 提取正文部分
            
            # 安全地解析 YAML 内容
            try:
                # 使用 safe_load 防止 YAML 注入攻击
                metadata = yaml.safe_load(frontmatter_yaml) or {}
                return metadata, remaining_content
            except yaml.YAMLError as e:
                # YAML 格式错误时的处理
                print(f"YAML解析错误: {e}")
                # 返回空元数据和原内容，避免数据丢失
                return {}, content
        else:
            # 没有找到 frontmatter 格式，可能是普通 Markdown 文件
            # 返回空元数据和原内容，保持向后兼容
            return {}, content
    
    @classmethod
    def parse_file(cls, file_path: Path) -> Tuple[Dict[str, Any], str]:
        """
        解析文件中的YAML frontmatter
        
        Args:
            file_path: 文件路径
            
        Returns:
            Tuple[metadata, content]: (元数据字典, 剩余内容)
        """
        utils_logger.info(f"开始解析文件: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            utils_logger.debug(f"成功读取文件，内容长度: {len(content)}")
            return cls.parse(content)
        except FileNotFoundError:
            utils_logger.error(f"文件不存在: {file_path}")
            return {}, ""
        except PermissionError:
            utils_logger.error(f"文件权限不足: {file_path}")
            return {}, ""
        except UnicodeDecodeError as e:
            utils_logger.error(f"文件编码错误: {file_path}, 错误: {e}")
            return {}, ""
        except Exception as e:
            utils_logger.error(f"读取文件失败: {file_path}, 错误: {e}", exc_info=True)
            return {}, ""
    
    @classmethod
    def has_frontmatter(cls, content: str) -> bool:
        """
        检查内容是否包含YAML frontmatter
        
        Args:
            content: 文件内容
            
        Returns:
            bool: 是否包含frontmatter
        """
        has_fm = bool(cls.FRONTMATTER_PATTERN.match(content))
        utils_logger.debug(f"检查 frontmatter 存在性: {has_fm}")
        return has_fm
    
    @classmethod
    def extract_metadata(cls, file_path: Path) -> Dict[str, Any]:
        """
        仅提取文件的元数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict[str, Any]: 元数据字典
        """
        utils_logger.debug(f"提取文件元数据: {file_path}")
        metadata, _ = cls.parse_file(file_path)
        utils_logger.debug(f"提取到的元数据: {metadata}")
        return metadata


def parse_markdown_with_frontmatter(file_path: Path) -> Dict[str, Any]:
    """解析Markdown文件，返回包含元数据和内容的完整信息
    
    这是一个便捷的包装函数，提供了比基本解析更丰富的返回信息。
    函数设计用于需要同时获取文件路径、frontmatter状态和完整内容的场景，
    特别适合在文档处理系统中批量处理文件。
    
    Args:
        file_path: Markdown文件路径对象，使用pathlib.Path提供跨平台兼容性
        
    Returns:
        Dict[str, Any]: 包含以下键的信息字典：
            - 'metadata': 解析出的YAML元数据字典，如果没有frontmatter则为空字典
            - 'content': 文件的正文内容（不包括frontmatter部分）
            - 'has_frontmatter': 布尔值，指示文件是否包含有效的frontmatter
            - 'file_path': 文件路径的字符串表示，便于日志记录和调试
            
    Examples:
        >>> from pathlib import Path
        >>> result = parse_markdown_with_frontmatter(Path("example.md"))
        >>> if result['has_frontmatter']:
        ...     print(f"标题: {result['metadata'].get('title')}")
        ...     print(f"作者: {result['metadata'].get('author')}")
        >>> print(f"内容长度: {len(result['content'])}")
        
    Note:
        - 该函数内部调用 FrontmatterParser.parse_file()，使用相同的解析逻辑
        - 返回的字典结构设计为易于序列化，适合在API响应中使用
        - file_path转换为字符串是为了确保JSON序列化时的兼容性
        - 即使文件读取失败，也会返回一个结构完整的字典（content为空字符串）
    """
    utils_logger.info(f"解析Markdown文件with frontmatter: {file_path}")
    
    # 使用核心解析器处理文件
    metadata, content = FrontmatterParser.parse_file(file_path)
    
    # 构建包含完整信息的返回字典
    result = {
        'metadata': metadata,          # YAML元数据字典
        'content': content,            # 纯正文内容
        'has_frontmatter': bool(metadata),  # 是否有frontmatter的布尔标志
        'file_path': str(file_path)    # 文件路径字符串
    }
    
    utils_logger.debug(f"解析结果 - has_frontmatter: {result['has_frontmatter']}, "
                      f"元数据键数量: {len(result['metadata'])}, "
                      f"内容长度: {len(result['content'])}")
    
    return result


def parse_frontmatter(file_path: Path) -> Dict[str, Any]:
    """解析文件的 YAML frontmatter（兼容函数）
    
    这是一个兼容性包装函数，为了保持与现有代码的兼容性而提供。
    内部直接调用 FrontmatterParser.parse_file() 方法。
    
    Args:
        file_path: 文件路径
        
    Returns:
        Dict[str, Any]: 解析结果，包含 metadata 和 content
        
    Note:
        此函数的存在是为了向后兼容，建议在新代码中使用
        FrontmatterParser.parse_file() 或 parse_markdown_with_frontmatter()
    """
    utils_logger.info(f"解析 frontmatter (兼容函数): {file_path}")
    
    # 使用核心解析器
    metadata, content = FrontmatterParser.parse_file(file_path)
    
    # 返回与原函数兼容的格式
    result = {
        'metadata': metadata,
        'content': content
    }
    
    utils_logger.debug(f"解析完成 - 元数据键: {list(metadata.keys()) if metadata else '无'}")
    return result