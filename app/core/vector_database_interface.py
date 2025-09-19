"""
向量数据库接口和实现
支持多种向量数据库：LanceDB、Chroma、Qdrant等
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import pandas as pd
import numpy as np
from datetime import datetime
import uuid
import os
import json
import logging

logger = logging.getLogger(__name__)


class VectorDatabaseType(str, Enum):
    """向量数据库类型"""
    LANCEDB = "lancedb"
    CHROMA = "chroma"
    QDRANT = "qdrant"
    FAISS = "faiss"
    MILVUS = "milvus"


class VectorDatabaseInterface(ABC):
    """向量数据库抽象接口"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_type = config.get("type")
        self.connection = None

    @abstractmethod
    async def initialize(self) -> bool:
        """初始化数据库连接"""
        pass

    @abstractmethod
    async def create_collection(self, name: str, schema: Dict[str, Any]) -> bool:
        """创建集合/表"""
        pass

    @abstractmethod
    async def collection_exists(self, name: str) -> bool:
        """检查集合/表是否存在"""
        pass

    @abstractmethod
    async def insert_data(self, collection_name: str, data: List[Dict[str, Any]]) -> bool:
        """插入数据"""
        pass

    @abstractmethod
    async def update_data(self, collection_name: str, data: List[Dict[str, Any]], conditions: Dict[str, Any]) -> bool:
        """更新数据"""
        pass

    @abstractmethod
    async def delete_data(self, collection_name: str, conditions: Dict[str, Any]) -> bool:
        """删除数据"""
        pass

    @abstractmethod
    async def search(self, collection_name: str, query_vector: List[float],
                    limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """向量搜索"""
        pass

    @abstractmethod
    async def query(self, collection_name: str, conditions: Optional[Dict[str, Any]] = None,
                   limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """条件查询"""
        pass

    @abstractmethod
    async def get_stats(self, collection_name: str) -> Dict[str, Any]:
        """获取集合统计信息"""
        pass

    @abstractmethod
    async def close(self):
        """关闭数据库连接"""
        pass


class LanceDBAdapter(VectorDatabaseInterface):
    """LanceDB 适配器"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.db_path = config.get("path", "./data/lancedb")
        self.db = None

    async def initialize(self) -> bool:
        """初始化LanceDB连接"""
        try:
            import lancedb
            os.makedirs(self.db_path, exist_ok=True)
            self.db = lancedb.connect(self.db_path)
            logger.info(f"LanceDB initialized at {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize LanceDB: {e}")
            return False

    async def create_collection(self, name: str, schema: Dict[str, Any]) -> bool:
        """创建LanceDB表"""
        try:
            # 检查表是否已存在
            if await self.collection_exists(name):
                return True

            # 记录schema信息，延迟创建表（在第一次插入数据时创建）
            logger.info(f"Schema registered for LanceDB table: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create LanceDB table {name}: {e}")
            return False

    async def collection_exists(self, name: str) -> bool:
        """检查LanceDB表是否存在"""
        try:
            self.db.open_table(name)
            return True
        except:
            return False

    async def insert_data(self, collection_name: str, data: List[Dict[str, Any]]) -> bool:
        """插入数据到LanceDB"""
        try:
            if not data:
                return True

            df = pd.DataFrame(data)

            # 确保数据类型正确
            for col_name in df.columns:
                if col_name.endswith('_count') or col_name.endswith('_size'):
                    df[col_name] = df[col_name].astype('Int64')
                elif col_name == 'embedding':
                    # 处理向量数据
                    df[col_name] = df[col_name].astype(object)
                else:
                    # 其他字段都转为字符串
                    df[col_name] = df[col_name].astype(str)

            # 尝试打开表，如果不存在则创建
            try:
                table = self.db.open_table(collection_name)
                table.add(df)
            except:
                # 表不存在，创建新表
                table = self.db.create_table(collection_name, df)
                logger.info(f"Created LanceDB table: {collection_name}")

            return True
        except Exception as e:
            logger.error(f"Failed to insert data into LanceDB table {collection_name}: {e}")
            return False

    async def update_data(self, collection_name: str, data: List[Dict[str, Any]], conditions: Dict[str, Any]) -> bool:
        """更新LanceDB数据（LanceDB不直接支持更新，需要删除后重新插入）"""
        try:
            # LanceDB的更新操作需要特殊处理
            # 这里暂时跳过实现，留待后续优化
            logger.warning("LanceDB update operation not implemented yet")
            return True
        except Exception as e:
            logger.error(f"Failed to update LanceDB data: {e}")
            return False

    async def delete_data(self, collection_name: str, conditions: Dict[str, Any]) -> bool:
        """删除LanceDB数据"""
        try:
            # LanceDB的删除操作需要特殊处理
            # 这里暂时跳过实现，留待后续优化
            logger.warning("LanceDB delete operation not implemented yet")
            return True
        except Exception as e:
            logger.error(f"Failed to delete LanceDB data: {e}")
            return False

    async def search(self, collection_name: str, query_vector: List[float],
                    limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """LanceDB向量搜索"""
        try:
            table = self.db.open_table(collection_name)
            # 执行向量搜索
            results = table.search(query_vector).limit(limit)

            if filters:
                # 应用过滤条件
                for key, value in filters.items():
                    results = results.where(f"{key} = '{value}'")

            return results.to_pandas().to_dict('records')
        except Exception as e:
            logger.error(f"Failed to search in LanceDB table {collection_name}: {e}")
            return []

    async def query(self, collection_name: str, conditions: Optional[Dict[str, Any]] = None,
                   limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """LanceDB条件查询"""
        try:
            table = self.db.open_table(collection_name)
            query = table.to_pandas()

            if conditions:
                # 应用条件过滤
                for key, value in conditions.items():
                    query = query[query[key] == value]

            if limit:
                query = query.head(limit)

            return query.to_dict('records')
        except Exception as e:
            logger.error(f"Failed to query LanceDB table {collection_name}: {e}")
            return []

    async def get_stats(self, collection_name: str) -> Dict[str, Any]:
        """获取LanceDB表统计信息"""
        try:
            table = self.db.open_table(collection_name)
            df = table.to_pandas()
            return {
                "total_rows": len(df),
                "columns": list(df.columns),
                "schema": str(table.schema)
            }
        except Exception as e:
            logger.error(f"Failed to get LanceDB stats for {collection_name}: {e}")
            return {}

    async def close(self):
        """关闭LanceDB连接"""
        try:
            if self.db:
                # LanceDB不需要显式关闭
                self.db = None
            logger.info("LanceDB connection closed")
        except Exception as e:
            logger.error(f"Error closing LanceDB: {e}")


class ChromaDBAdapter(VectorDatabaseInterface):
    """ChromaDB 适配器"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 8000)
        self.client = None

    async def initialize(self) -> bool:
        """初始化ChromaDB连接"""
        try:
            import chromadb
            self.client = chromadb.HttpClient(host=self.host, port=self.port)
            logger.info(f"ChromaDB initialized at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            return False

    async def create_collection(self, name: str, schema: Dict[str, Any]) -> bool:
        """创建ChromaDB集合"""
        try:
            collection = self.client.create_collection(name=name)
            logger.info(f"Created ChromaDB collection: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create ChromaDB collection {name}: {e}")
            return False

    async def collection_exists(self, name: str) -> bool:
        """检查ChromaDB集合是否存在"""
        try:
            self.client.get_collection(name=name)
            return True
        except:
            return False

    async def insert_data(self, collection_name: str, data: List[Dict[str, Any]]) -> bool:
        """插入数据到ChromaDB"""
        try:
            collection = self.client.get_or_create_collection(name=collection_name)

            # 准备ChromaDB所需的数据格式
            ids = []
            embeddings = []
            metadatas = []
            documents = []

            for item in data:
                ids.append(item.get("id", str(uuid.uuid4())))
                if "embedding" in item:
                    embeddings.append(item["embedding"])
                metadatas.append({k: v for k, v in item.items() if k not in ["id", "embedding", "content"]})
                documents.append(item.get("content", ""))

            collection.add(
                ids=ids,
                embeddings=embeddings if embeddings else None,
                metadatas=metadatas,
                documents=documents
            )
            return True
        except Exception as e:
            logger.error(f"Failed to insert data into ChromaDB collection {collection_name}: {e}")
            return False

    # 实现其他方法...
    async def update_data(self, collection_name: str, data: List[Dict[str, Any]], conditions: Dict[str, Any]) -> bool:
        logger.warning("ChromaDB update not implemented yet")
        return True

    async def delete_data(self, collection_name: str, conditions: Dict[str, Any]) -> bool:
        logger.warning("ChromaDB delete not implemented yet")
        return True

    async def search(self, collection_name: str, query_vector: List[float],
                    limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        try:
            collection = self.client.get_collection(name=collection_name)
            results = collection.query(
                query_embeddings=[query_vector],
                n_results=limit,
                where=filters
            )
            return results
        except Exception as e:
            logger.error(f"Failed to search in ChromaDB collection {collection_name}: {e}")
            return []

    async def query(self, collection_name: str, conditions: Optional[Dict[str, Any]] = None,
                   limit: Optional[int] = None) -> List[Dict[str, Any]]:
        logger.warning("ChromaDB query not implemented yet")
        return []

    async def get_stats(self, collection_name: str) -> Dict[str, Any]:
        try:
            collection = self.client.get_collection(name=collection_name)
            return {"total_count": collection.count()}
        except Exception as e:
            logger.error(f"Failed to get ChromaDB stats for {collection_name}: {e}")
            return {}

    async def close(self):
        if self.client:
            self.client = None
        logger.info("ChromaDB connection closed")


class VectorDatabaseFactory:
    """向量数据库工厂类"""

    @staticmethod
    def create_database(config: Dict[str, Any]) -> VectorDatabaseInterface:
        """根据配置创建对应的向量数据库实例"""
        db_type = config.get("type", VectorDatabaseType.LANCEDB)

        if db_type == VectorDatabaseType.LANCEDB:
            return LanceDBAdapter(config)
        elif db_type == VectorDatabaseType.CHROMA:
            return ChromaDBAdapter(config)
        # elif db_type == VectorDatabaseType.QDRANT:
        #     return QdrantAdapter(config)
        # elif db_type == VectorDatabaseType.FAISS:
        #     return FAISSAdapter(config)
        else:
            raise ValueError(f"Unsupported vector database type: {db_type}")

    @staticmethod
    def get_supported_databases() -> List[Dict[str, Any]]:
        """获取支持的向量数据库列表"""
        return [
            {
                "type": VectorDatabaseType.LANCEDB,
                "name": "LanceDB",
                "description": "高性能向量数据库，适合本地部署",
                "default_config": {
                    "type": VectorDatabaseType.LANCEDB,
                    "path": "./data/lancedb"
                }
            },
            {
                "type": VectorDatabaseType.CHROMA,
                "name": "ChromaDB",
                "description": "开源向量数据库，易于使用",
                "default_config": {
                    "type": VectorDatabaseType.CHROMA,
                    "host": "localhost",
                    "port": 8000
                }
            }
            # 可以添加更多数据库支持
        ]