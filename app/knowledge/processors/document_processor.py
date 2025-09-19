"""
文档处理器，支持多种文件格式
"""
import os
from pathlib import Path
from typing import Optional
import aiofiles
import logging

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """文档处理器，支持多种文件格式"""

    @staticmethod
    async def extract_text_from_file(file_path: str) -> str:
        """从文件中提取文本内容"""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()

        try:
            if extension == '.txt':
                return await DocumentProcessor._process_txt(file_path)
            elif extension == '.md':
                return await DocumentProcessor._process_markdown(file_path)
            elif extension == '.pdf':
                return await DocumentProcessor._process_pdf(file_path)
            elif extension in ['.doc', '.docx']:
                return await DocumentProcessor._process_docx(file_path)
            elif extension in ['.html', '.htm']:
                return await DocumentProcessor._process_html(file_path)
            else:
                logger.warning(f"Unsupported file format: {extension}")
                return ""
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return ""

    @staticmethod
    async def _process_txt(file_path: Path) -> str:
        """处理文本文件"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                return await f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                async with aiofiles.open(file_path, 'r', encoding='gbk') as f:
                    return await f.read()
            except:
                async with aiofiles.open(file_path, 'r', encoding='latin-1') as f:
                    return await f.read()

    @staticmethod
    async def _process_markdown(file_path: Path) -> str:
        """处理Markdown文件"""
        return await DocumentProcessor._process_txt(file_path)

    @staticmethod
    async def _process_pdf(file_path: Path) -> str:
        """处理PDF文件"""
        text = ""
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
        return text

    @staticmethod
    async def _process_docx(file_path: Path) -> str:
        """处理Word文档"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error processing DOCX {file_path}: {e}")
            return ""

    @staticmethod
    async def _process_html(file_path: Path) -> str:
        """处理HTML文件"""
        try:
            import markdownify
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                html_content = await f.read()
                return markdownify.markdownify(html_content)
        except Exception as e:
            logger.error(f"Error processing HTML {file_path}: {e}")
            return ""

    @staticmethod
    def get_supported_extensions() -> set:
        """获取支持的文件扩展名"""
        return {'.txt', '.md', '.pdf', '.doc', '.docx', '.html', '.htm'}