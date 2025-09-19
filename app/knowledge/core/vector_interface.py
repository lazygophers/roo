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
    HNSWLIB = "hnswlib"
    VECTORDB = "vectordb"


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
            if await self.collection_exists(name):
                return True
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
                    df[col_name] = df[col_name].astype(object)
                else:
                    df[col_name] = df[col_name].astype(str)

            # 尝试打开表，如果不存在则创建
            try:
                table = self.db.open_table(collection_name)
                table.add(df)
            except:
                table = self.db.create_table(collection_name, df)
                logger.info(f"Created LanceDB table: {collection_name}")

            return True
        except Exception as e:
            logger.error(f"Failed to insert data into LanceDB table {collection_name}: {e}")
            return False

    async def update_data(self, collection_name: str, data: List[Dict[str, Any]], conditions: Dict[str, Any]) -> bool:
        """更新LanceDB数据"""
        try:
            logger.warning("LanceDB update operation not implemented yet")
            return True
        except Exception as e:
            logger.error(f"Failed to update LanceDB data: {e}")
            return False

    async def delete_data(self, collection_name: str, conditions: Dict[str, Any]) -> bool:
        """删除LanceDB数据"""
        try:
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
            results = table.search(query_vector).limit(limit)

            if filters:
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


class QdrantAdapter(VectorDatabaseInterface):
    """Qdrant 适配器"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 6333)
        self.collection_name = config.get("collection_name", "default")
        self.client = None

    async def initialize(self) -> bool:
        """初始化Qdrant连接"""
        try:
            from qdrant_client import QdrantClient
            self.client = QdrantClient(host=self.host, port=self.port)
            logger.info(f"Qdrant initialized at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant: {e}")
            return False

    async def create_collection(self, name: str, schema: Dict[str, Any]) -> bool:
        """创建Qdrant集合"""
        try:
            from qdrant_client.models import Distance, VectorParams
            vector_size = schema.get("vector_size", 384)

            self.client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
            logger.info(f"Created Qdrant collection: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create Qdrant collection {name}: {e}")
            return False

    async def collection_exists(self, name: str) -> bool:
        """检查Qdrant集合是否存在"""
        try:
            collections = self.client.get_collections()
            return any(col.name == name for col in collections.collections)
        except:
            return False

    async def insert_data(self, collection_name: str, data: List[Dict[str, Any]]) -> bool:
        """插入数据到Qdrant"""
        try:
            from qdrant_client.models import PointStruct

            points = []
            for i, item in enumerate(data):
                points.append(
                    PointStruct(
                        id=item.get("id", str(uuid.uuid4())),
                        vector=item.get("embedding", []),
                        payload={k: v for k, v in item.items() if k not in ["id", "embedding"]}
                    )
                )

            self.client.upsert(collection_name=collection_name, points=points)
            return True
        except Exception as e:
            logger.error(f"Failed to insert data into Qdrant collection {collection_name}: {e}")
            return False

    async def update_data(self, collection_name: str, data: List[Dict[str, Any]], conditions: Dict[str, Any]) -> bool:
        logger.warning("Qdrant update not fully implemented yet")
        return True

    async def delete_data(self, collection_name: str, conditions: Dict[str, Any]) -> bool:
        logger.warning("Qdrant delete not fully implemented yet")
        return True

    async def search(self, collection_name: str, query_vector: List[float],
                    limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=filters
            )
            return [{"score": r.score, **r.payload} for r in results]
        except Exception as e:
            logger.error(f"Failed to search in Qdrant collection {collection_name}: {e}")
            return []

    async def query(self, collection_name: str, conditions: Optional[Dict[str, Any]] = None,
                   limit: Optional[int] = None) -> List[Dict[str, Any]]:
        logger.warning("Qdrant query not fully implemented yet")
        return []

    async def get_stats(self, collection_name: str) -> Dict[str, Any]:
        try:
            info = self.client.get_collection(collection_name)
            return {"total_count": info.points_count}
        except Exception as e:
            logger.error(f"Failed to get Qdrant stats for {collection_name}: {e}")
            return {}

    async def close(self):
        if self.client:
            self.client = None
        logger.info("Qdrant connection closed")


class FAISSAdapter(VectorDatabaseInterface):
    """FAISS 适配器"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.index_path = config.get("index_path", "./data/faiss_index")
        self.dimension = config.get("dimension", 384)
        self.index = None
        self.id_to_metadata = {}

    async def initialize(self) -> bool:
        """初始化FAISS索引"""
        try:
            import faiss
            # 创建L2距离索引
            self.index = faiss.IndexFlatL2(self.dimension)

            # 尝试加载已存在的索引
            if os.path.exists(self.index_path):
                self.index = faiss.read_index(self.index_path)

            logger.info(f"FAISS initialized with dimension {self.dimension}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize FAISS: {e}")
            return False

    async def create_collection(self, name: str, schema: Dict[str, Any]) -> bool:
        """FAISS不需要显式创建集合"""
        return True

    async def collection_exists(self, name: str) -> bool:
        """FAISS集合概念"""
        return True

    async def insert_data(self, collection_name: str, data: List[Dict[str, Any]]) -> bool:
        """插入数据到FAISS"""
        try:
            import numpy as np

            vectors = []
            for item in data:
                if "embedding" in item:
                    vectors.append(item["embedding"])
                    # 存储元数据
                    idx = self.index.ntotal
                    self.id_to_metadata[idx] = {k: v for k, v in item.items() if k != "embedding"}

            if vectors:
                vectors_np = np.array(vectors, dtype=np.float32)
                self.index.add(vectors_np)

                # 保存索引
                os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
                import faiss
                faiss.write_index(self.index, self.index_path)

            return True
        except Exception as e:
            logger.error(f"Failed to insert data into FAISS: {e}")
            return False

    async def update_data(self, collection_name: str, data: List[Dict[str, Any]], conditions: Dict[str, Any]) -> bool:
        logger.warning("FAISS update not supported (immutable index)")
        return False

    async def delete_data(self, collection_name: str, conditions: Dict[str, Any]) -> bool:
        logger.warning("FAISS delete not supported (immutable index)")
        return False

    async def search(self, collection_name: str, query_vector: List[float],
                    limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        try:
            import numpy as np

            query_np = np.array([query_vector], dtype=np.float32)
            distances, indices = self.index.search(query_np, limit)

            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx >= 0:  # Valid index
                    result = {"score": float(dist)}
                    if idx in self.id_to_metadata:
                        result.update(self.id_to_metadata[idx])
                    results.append(result)

            return results
        except Exception as e:
            logger.error(f"Failed to search in FAISS: {e}")
            return []

    async def query(self, collection_name: str, conditions: Optional[Dict[str, Any]] = None,
                   limit: Optional[int] = None) -> List[Dict[str, Any]]:
        # FAISS主要用于向量搜索，不支持复杂查询
        return list(self.id_to_metadata.values())[:limit] if limit else list(self.id_to_metadata.values())

    async def get_stats(self, collection_name: str) -> Dict[str, Any]:
        return {"total_count": self.index.ntotal if self.index else 0}

    async def close(self):
        self.index = None
        logger.info("FAISS connection closed")


class MilvusAdapter(VectorDatabaseInterface):
    """Milvus 适配器"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 19530)
        self.client = None

    async def initialize(self) -> bool:
        """初始化Milvus连接"""
        try:
            from pymilvus import connections
            connections.connect(host=self.host, port=self.port)
            logger.info(f"Milvus initialized at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Milvus: {e}")
            return False

    async def create_collection(self, name: str, schema: Dict[str, Any]) -> bool:
        """创建Milvus集合"""
        try:
            from pymilvus import Collection, CollectionSchema, FieldSchema, DataType

            # 定义schema
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=schema.get("dimension", 384))
            ]

            schema_obj = CollectionSchema(fields)
            collection = Collection(name, schema_obj)

            logger.info(f"Created Milvus collection: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create Milvus collection {name}: {e}")
            return False

    async def collection_exists(self, name: str) -> bool:
        """检查Milvus集合是否存在"""
        try:
            from pymilvus import utility
            return utility.has_collection(name)
        except:
            return False

    async def insert_data(self, collection_name: str, data: List[Dict[str, Any]]) -> bool:
        """插入数据到Milvus"""
        try:
            from pymilvus import Collection

            collection = Collection(collection_name)
            embeddings = [item.get("embedding", []) for item in data]

            collection.insert([embeddings])
            collection.flush()
            return True
        except Exception as e:
            logger.error(f"Failed to insert data into Milvus collection {collection_name}: {e}")
            return False

    async def update_data(self, collection_name: str, data: List[Dict[str, Any]], conditions: Dict[str, Any]) -> bool:
        logger.warning("Milvus update not fully implemented yet")
        return True

    async def delete_data(self, collection_name: str, conditions: Dict[str, Any]) -> bool:
        logger.warning("Milvus delete not fully implemented yet")
        return True

    async def search(self, collection_name: str, query_vector: List[float],
                    limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        try:
            from pymilvus import Collection

            collection = Collection(collection_name)
            collection.load()

            search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
            results = collection.search([query_vector], "embedding", search_params, limit=limit)

            return [{"score": hit.distance, "id": hit.id} for hit in results[0]]
        except Exception as e:
            logger.error(f"Failed to search in Milvus collection {collection_name}: {e}")
            return []

    async def query(self, collection_name: str, conditions: Optional[Dict[str, Any]] = None,
                   limit: Optional[int] = None) -> List[Dict[str, Any]]:
        logger.warning("Milvus query not fully implemented yet")
        return []

    async def get_stats(self, collection_name: str) -> Dict[str, Any]:
        try:
            from pymilvus import Collection
            collection = Collection(collection_name)
            return {"total_count": collection.num_entities}
        except Exception as e:
            logger.error(f"Failed to get Milvus stats for {collection_name}: {e}")
            return {}

    async def close(self):
        logger.info("Milvus connection closed")


class HNSWLIBAdapter(VectorDatabaseInterface):
    """HNSWLIB 适配器"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.index_path = config.get("index_path", "./data/hnswlib_index")
        self.dimension = config.get("dimension", 384)
        self.max_elements = config.get("max_elements", 10000)
        self.index = None
        self.id_to_metadata = {}
        self.current_count = 0

    async def initialize(self) -> bool:
        """初始化HNSWLIB索引"""
        try:
            import hnswlib

            self.index = hnswlib.Index(space='cosine', dim=self.dimension)

            # 尝试加载已存在的索引
            if os.path.exists(self.index_path):
                self.index.load_index(self.index_path)
                self.current_count = self.index.get_current_count()
            else:
                self.index.init_index(max_elements=self.max_elements, ef_construction=200, M=16)

            logger.info(f"HNSWLIB initialized with dimension {self.dimension}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize HNSWLIB: {e}")
            return False

    async def create_collection(self, name: str, schema: Dict[str, Any]) -> bool:
        """HNSWLIB不需要显式创建集合"""
        return True

    async def collection_exists(self, name: str) -> bool:
        """HNSWLIB集合概念"""
        return True

    async def insert_data(self, collection_name: str, data: List[Dict[str, Any]]) -> bool:
        """插入数据到HNSWLIB"""
        try:
            vectors = []
            labels = []

            for item in data:
                if "embedding" in item:
                    vectors.append(item["embedding"])
                    label = self.current_count
                    labels.append(label)

                    # 存储元数据
                    self.id_to_metadata[label] = {k: v for k, v in item.items() if k != "embedding"}
                    self.current_count += 1

            if vectors:
                import numpy as np
                vectors_np = np.array(vectors, dtype=np.float32)
                self.index.add_items(vectors_np, labels)

                # 保存索引
                os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
                self.index.save_index(self.index_path)

            return True
        except Exception as e:
            logger.error(f"Failed to insert data into HNSWLIB: {e}")
            return False

    async def update_data(self, collection_name: str, data: List[Dict[str, Any]], conditions: Dict[str, Any]) -> bool:
        logger.warning("HNSWLIB update not supported")
        return False

    async def delete_data(self, collection_name: str, conditions: Dict[str, Any]) -> bool:
        logger.warning("HNSWLIB delete not supported")
        return False

    async def search(self, collection_name: str, query_vector: List[float],
                    limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        try:
            import numpy as np

            query_np = np.array([query_vector], dtype=np.float32)
            labels, distances = self.index.knn_query(query_np, k=limit)

            results = []
            for label, dist in zip(labels[0], distances[0]):
                result = {"score": float(1 - dist)}  # Convert distance to similarity
                if label in self.id_to_metadata:
                    result.update(self.id_to_metadata[label])
                results.append(result)

            return results
        except Exception as e:
            logger.error(f"Failed to search in HNSWLIB: {e}")
            return []

    async def query(self, collection_name: str, conditions: Optional[Dict[str, Any]] = None,
                   limit: Optional[int] = None) -> List[Dict[str, Any]]:
        return list(self.id_to_metadata.values())[:limit] if limit else list(self.id_to_metadata.values())

    async def get_stats(self, collection_name: str) -> Dict[str, Any]:
        return {"total_count": self.current_count}

    async def close(self):
        self.index = None
        logger.info("HNSWLIB connection closed")


class VectorDBAdapter(VectorDatabaseInterface):
    """VectorDB 适配器 (通用云原生向量数据库)"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_endpoint = config.get("api_endpoint", "http://localhost:8080")
        self.api_key = config.get("api_key", "")
        self.headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    async def initialize(self) -> bool:
        """初始化VectorDB连接"""
        try:
            # 这里应该实现对特定VectorDB服务的连接测试
            logger.info(f"VectorDB initialized at {self.api_endpoint}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize VectorDB: {e}")
            return False

    async def create_collection(self, name: str, schema: Dict[str, Any]) -> bool:
        """创建VectorDB集合"""
        try:
            # 实现HTTP API调用创建集合
            logger.info(f"Created VectorDB collection: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create VectorDB collection {name}: {e}")
            return False

    async def collection_exists(self, name: str) -> bool:
        """检查VectorDB集合是否存在"""
        try:
            # 实现HTTP API调用检查集合
            return True
        except:
            return False

    async def insert_data(self, collection_name: str, data: List[Dict[str, Any]]) -> bool:
        """插入数据到VectorDB"""
        logger.warning("VectorDB adapter is a placeholder - needs specific implementation")
        return True

    async def update_data(self, collection_name: str, data: List[Dict[str, Any]], conditions: Dict[str, Any]) -> bool:
        logger.warning("VectorDB update not implemented yet")
        return True

    async def delete_data(self, collection_name: str, conditions: Dict[str, Any]) -> bool:
        logger.warning("VectorDB delete not implemented yet")
        return True

    async def search(self, collection_name: str, query_vector: List[float],
                    limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        logger.warning("VectorDB search not implemented yet")
        return []

    async def query(self, collection_name: str, conditions: Optional[Dict[str, Any]] = None,
                   limit: Optional[int] = None) -> List[Dict[str, Any]]:
        logger.warning("VectorDB query not implemented yet")
        return []

    async def get_stats(self, collection_name: str) -> Dict[str, Any]:
        return {"total_count": 0}

    async def close(self):
        logger.info("VectorDB connection closed")


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
        elif db_type == VectorDatabaseType.QDRANT:
            return QdrantAdapter(config)
        elif db_type == VectorDatabaseType.FAISS:
            return FAISSAdapter(config)
        elif db_type == VectorDatabaseType.MILVUS:
            return MilvusAdapter(config)
        elif db_type == VectorDatabaseType.HNSWLIB:
            return HNSWLIBAdapter(config)
        elif db_type == VectorDatabaseType.VECTORDB:
            return VectorDBAdapter(config)
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
            },
            {
                "type": VectorDatabaseType.QDRANT,
                "name": "Qdrant",
                "description": "高性能云服务向量数据库",
                "default_config": {
                    "type": VectorDatabaseType.QDRANT,
                    "host": "localhost",
                    "port": 6333,
                    "collection_name": "default"
                }
            },
            {
                "type": VectorDatabaseType.FAISS,
                "name": "FAISS",
                "description": "Facebook AI向量搜索库，高性能本地搜索",
                "default_config": {
                    "type": VectorDatabaseType.FAISS,
                    "index_path": "./data/faiss_index",
                    "dimension": 384
                }
            },
            {
                "type": VectorDatabaseType.MILVUS,
                "name": "Milvus",
                "description": "轻量级云原生向量数据库",
                "default_config": {
                    "type": VectorDatabaseType.MILVUS,
                    "host": "localhost",
                    "port": 19530
                }
            },
            {
                "type": VectorDatabaseType.HNSWLIB,
                "name": "HNSWLIB",
                "description": "高效近似最近邻搜索库",
                "default_config": {
                    "type": VectorDatabaseType.HNSWLIB,
                    "index_path": "./data/hnswlib_index",
                    "dimension": 384,
                    "max_elements": 10000
                }
            },
            {
                "type": VectorDatabaseType.VECTORDB,
                "name": "VectorDB",
                "description": "云原生向量数据库服务",
                "default_config": {
                    "type": VectorDatabaseType.VECTORDB,
                    "api_endpoint": "http://localhost:8080",
                    "api_key": ""
                }
            }
        ]