"""
知识库服务模块
支持本地文件作为RAG源，使用LanceDB作为向量存储
"""
import os
import json
import hashlib
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import aiofiles
import lancedb
from sentence_transformers import SentenceTransformer
import PyPDF2
from docx import Document
import markdownify

from app.core.config import PROJECT_ROOT
from app.core.logging import setup_logging

logger = setup_logging()

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
            elif extension == '.html':
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
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            return await f.read()

    @staticmethod
    async def _process_markdown(file_path: Path) -> str:
        """处理Markdown文件"""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            return await f.read()

    @staticmethod
    async def _process_pdf(file_path: Path) -> str:
        """处理PDF文件"""
        text = ""
        try:
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
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                html_content = await f.read()
                return markdownify.markdownify(html_content)
        except Exception as e:
            logger.error(f"Error processing HTML {file_path}: {e}")
            return ""

class TextChunker:
    """文本分块器"""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """将文本分割成块"""
        if not text.strip():
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # 如果不是最后一块，尝试在句号、换行符处分割
            if end < len(text):
                # 向后查找合适的分割点
                for i in range(end, max(start + self.chunk_size // 2, end - 100), -1):
                    if text[i] in '.!?\n':
                        end = i + 1
                        break

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunk_metadata = metadata.copy() if metadata else {}
                chunk_metadata.update({
                    'chunk_index': len(chunks),
                    'chunk_start': start,
                    'chunk_end': end,
                    'chunk_size': len(chunk_text)
                })

                chunks.append({
                    'text': chunk_text,
                    'metadata': chunk_metadata
                })

            start = end - self.chunk_overlap

        return chunks

class KnowledgeBaseService:
    """知识库服务"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.path.join(PROJECT_ROOT, "data", "knowledge_base")
        self.db = None
        self.model = None
        self.chunker = TextChunker()
        self.supported_extensions = {'.txt', '.md', '.pdf', '.doc', '.docx', '.html'}

        # 确保数据库目录存在
        os.makedirs(self.db_path, exist_ok=True)

    async def initialize(self):
        """初始化知识库服务"""
        try:
            # 初始化LanceDB
            self.db = lancedb.connect(self.db_path)

            # 初始化嵌入模型
            logger.info("Loading sentence transformer model...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')

            # 创建表格（如果不存在）
            await self._ensure_tables_exist()

            logger.info("Knowledge base service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize knowledge base service: {e}")
            raise

    async def _ensure_tables_exist(self):
        """确保所需的表格存在"""
        try:
            # 尝试获取documents表，如果不存在则创建
            try:
                self.documents_table = self.db.open_table("documents")
            except:
                # 创建documents表的schema
                schema = [
                    {"name": "id", "type": "string"},
                    {"name": "content", "type": "string"},
                    {"name": "vector", "type": "vector(384)"},  # all-MiniLM-L6-v2的维度
                    {"name": "metadata", "type": "string"},  # JSON字符串
                    {"name": "file_path", "type": "string"},
                    {"name": "file_hash", "type": "string"},
                    {"name": "chunk_index", "type": "int"},
                    {"name": "created_at", "type": "string"},
                ]

                # 创建空表
                import pandas as pd
                empty_df = pd.DataFrame({col["name"]: [] for col in schema})
                empty_df["vector"] = empty_df["vector"].astype(object)

                self.documents_table = self.db.create_table("documents", empty_df)
                logger.info("Created documents table")
        except Exception as e:
            logger.error(f"Error ensuring tables exist: {e}")
            raise

    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件哈希"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    async def add_document(self, file_path: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """添加文档到知识库"""
        try:
            file_path = Path(file_path).resolve()

            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            if file_path.suffix.lower() not in self.supported_extensions:
                raise ValueError(f"Unsupported file type: {file_path.suffix}")

            # 计算文件哈希
            file_hash = self._calculate_file_hash(str(file_path))

            # 检查文件是否已经存在
            existing_docs = self.documents_table.search().where(f"file_hash = '{file_hash}'").limit(1).to_list()
            if existing_docs:
                logger.info(f"Document already exists: {file_path}")
                return {"status": "already_exists", "file_path": str(file_path)}

            # 提取文本内容
            logger.info(f"Processing document: {file_path}")
            text_content = await DocumentProcessor.extract_text_from_file(str(file_path))

            if not text_content.strip():
                raise ValueError("No text content extracted from file")

            # 准备元数据
            doc_metadata = {
                "file_name": file_path.name,
                "file_path": str(file_path),
                "file_size": file_path.stat().st_size,
                "file_type": file_path.suffix.lower(),
                "processed_at": datetime.now().isoformat()
            }
            if metadata:
                doc_metadata.update(metadata)

            # 分割文本
            chunks = self.chunker.chunk_text(text_content, doc_metadata)
            logger.info(f"Split document into {len(chunks)} chunks")

            # 生成嵌入向量并保存到数据库
            documents_to_add = []
            for chunk in chunks:
                embedding = self.model.encode(chunk['text'])

                doc_data = {
                    "id": f"{file_hash}_{chunk['metadata']['chunk_index']}",
                    "content": chunk['text'],
                    "vector": embedding.tolist(),
                    "metadata": json.dumps(chunk['metadata']),
                    "file_path": str(file_path),
                    "file_hash": file_hash,
                    "chunk_index": chunk['metadata']['chunk_index'],
                    "created_at": datetime.now().isoformat()
                }
                documents_to_add.append(doc_data)

            # 批量插入
            import pandas as pd
            df = pd.DataFrame(documents_to_add)
            self.documents_table.add(df)

            logger.info(f"Successfully added document: {file_path}")
            return {
                "status": "success",
                "file_path": str(file_path),
                "chunks_count": len(chunks),
                "file_hash": file_hash
            }

        except Exception as e:
            logger.error(f"Error adding document {file_path}: {e}")
            raise

    async def search_documents(self, query: str, limit: int = 10, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """搜索相关文档"""
        try:
            # 生成查询向量
            query_embedding = self.model.encode(query)

            # 在LanceDB中搜索
            results = (
                self.documents_table
                .search(query_embedding.tolist())
                .limit(limit)
                .to_list()
            )

            # 处理结果
            formatted_results = []
            for result in results:
                # 解析元数据
                metadata = json.loads(result.get('metadata', '{}'))

                formatted_result = {
                    'content': result.get('content', ''),
                    'score': float(result.get('_distance', 0)),
                    'metadata': metadata,
                    'file_path': result.get('file_path', ''),
                    'chunk_index': result.get('chunk_index', 0)
                }

                # 过滤低分结果
                if formatted_result['score'] >= threshold:
                    formatted_results.append(formatted_result)

            return formatted_results

        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            raise

    async def list_documents(self) -> List[Dict[str, Any]]:
        """列出所有文档"""
        try:
            # 获取所有唯一的文档
            all_docs = self.documents_table.search().limit(10000).to_list()

            # 按文件路径分组
            docs_by_file = {}
            for doc in all_docs:
                file_path = doc.get('file_path', '')
                if file_path not in docs_by_file:
                    metadata = json.loads(doc.get('metadata', '{}'))
                    docs_by_file[file_path] = {
                        'file_path': file_path,
                        'file_hash': doc.get('file_hash', ''),
                        'file_name': metadata.get('file_name', Path(file_path).name),
                        'file_size': metadata.get('file_size', 0),
                        'file_type': metadata.get('file_type', ''),
                        'chunks_count': 0,
                        'created_at': doc.get('created_at', ''),
                        'processed_at': metadata.get('processed_at', '')
                    }
                docs_by_file[file_path]['chunks_count'] += 1

            return list(docs_by_file.values())

        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []

    async def delete_document(self, file_path: str) -> Dict[str, Any]:
        """删除文档"""
        try:
            # 删除相关的所有块
            self.documents_table.delete(f"file_path = '{file_path}'")

            logger.info(f"Successfully deleted document: {file_path}")
            return {"status": "success", "file_path": file_path}

        except Exception as e:
            logger.error(f"Error deleting document {file_path}: {e}")
            raise

    async def get_supported_formats(self) -> List[str]:
        """获取支持的文件格式"""
        return list(self.supported_extensions)

# 全局知识库服务实例
_knowledge_base_service = None

def init_knowledge_base_service() -> KnowledgeBaseService:
    """初始化知识库服务"""
    global _knowledge_base_service
    if _knowledge_base_service is None:
        _knowledge_base_service = KnowledgeBaseService()
    return _knowledge_base_service

def get_knowledge_base_service() -> KnowledgeBaseService:
    """获取知识库服务实例"""
    if _knowledge_base_service is None:
        return init_knowledge_base_service()
    return _knowledge_base_service