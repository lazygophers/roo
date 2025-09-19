"""
嵌入模型接口和提供商实现
支持多种嵌入服务：本地、OpenAI、Azure OpenAI、HuggingFace等
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EmbeddingProvider(str, Enum):
    """嵌入模型提供商类型"""
    LOCAL = "local"
    OPENAI = "openai"
    AZURE = "azure"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"


class EmbeddingInterface(ABC):
    """嵌入模型抽象接口"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider = config.get("provider")
        self.model = config.get("model")

    @abstractmethod
    async def initialize(self) -> bool:
        """初始化嵌入模型"""
        pass

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """嵌入单个文本"""
        pass

    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入文本"""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """获取嵌入向量维度"""
        pass

    @abstractmethod
    async def close(self):
        """关闭连接"""
        pass


class LocalEmbeddingAdapter(EmbeddingInterface):
    """本地嵌入模型适配器（使用SentenceTransformers）"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model_instance = None

    async def initialize(self) -> bool:
        """初始化本地嵌入模型"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model_instance = SentenceTransformer(self.model)
            logger.info(f"Local embedding model initialized: {self.model}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize local embedding model: {e}")
            return False

    async def embed_text(self, text: str) -> List[float]:
        """嵌入单个文本"""
        try:
            embedding = self.model_instance.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to embed text: {e}")
            return []

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入文本"""
        try:
            embeddings = self.model_instance.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Failed to embed texts: {e}")
            return []

    def get_dimension(self) -> int:
        """获取嵌入向量维度"""
        if self.model_instance:
            return self.model_instance.get_sentence_embedding_dimension()
        return 384  # 默认维度

    async def close(self):
        """关闭本地模型"""
        self.model_instance = None
        logger.info("Local embedding model closed")


class OpenAIEmbeddingAdapter(EmbeddingInterface):
    """OpenAI嵌入模型适配器"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", "https://api.openai.com/v1")
        self.client = None

    async def initialize(self) -> bool:
        """初始化OpenAI客户端"""
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            logger.info(f"OpenAI embedding initialized: {self.model}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI embedding: {e}")
            return False

    async def embed_text(self, text: str) -> List[float]:
        """嵌入单个文本"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to embed text with OpenAI: {e}")
            return []

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入文本"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"Failed to embed texts with OpenAI: {e}")
            return []

    def get_dimension(self) -> int:
        """获取嵌入向量维度"""
        # OpenAI嵌入模型的维度映射
        dimension_map = {
            "text-embedding-ada-002": 1536,
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
        }
        return dimension_map.get(self.model, 1536)

    async def close(self):
        """关闭OpenAI客户端"""
        self.client = None
        logger.info("OpenAI embedding client closed")


class AzureEmbeddingAdapter(EmbeddingInterface):
    """Azure OpenAI嵌入模型适配器"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.azure_endpoint = config.get("base_url")
        self.api_version = config.get("api_version", "2023-05-15")
        self.client = None

    async def initialize(self) -> bool:
        """初始化Azure OpenAI客户端"""
        try:
            import openai
            self.client = openai.AzureOpenAI(
                api_key=self.api_key,
                azure_endpoint=self.azure_endpoint,
                api_version=self.api_version
            )
            logger.info(f"Azure OpenAI embedding initialized: {self.model}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI embedding: {e}")
            return False

    async def embed_text(self, text: str) -> List[float]:
        """嵌入单个文本"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to embed text with Azure OpenAI: {e}")
            return []

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入文本"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"Failed to embed texts with Azure OpenAI: {e}")
            return []

    def get_dimension(self) -> int:
        """获取嵌入向量维度"""
        # Azure OpenAI与OpenAI相同的模型维度
        dimension_map = {
            "text-embedding-ada-002": 1536,
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
        }
        return dimension_map.get(self.model, 1536)

    async def close(self):
        """关闭Azure OpenAI客户端"""
        self.client = None
        logger.info("Azure OpenAI embedding client closed")


class HuggingFaceEmbeddingAdapter(EmbeddingInterface):
    """HuggingFace嵌入模型适配器"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", "https://api-inference.huggingface.co")

    async def initialize(self) -> bool:
        """初始化HuggingFace客户端"""
        try:
            import requests
            self.session = requests.Session()
            if self.api_key:
                self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
            logger.info(f"HuggingFace embedding initialized: {self.model}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize HuggingFace embedding: {e}")
            return False

    async def embed_text(self, text: str) -> List[float]:
        """嵌入单个文本"""
        try:
            import requests
            url = f"{self.base_url}/pipeline/feature-extraction/{self.model}"

            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                json={"inputs": text}
            )
            response.raise_for_status()

            embeddings = response.json()
            # HuggingFace返回的可能是多维数组，需要处理
            if isinstance(embeddings[0], list):
                return embeddings[0]
            return embeddings
        except Exception as e:
            logger.error(f"Failed to embed text with HuggingFace: {e}")
            return []

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量嵌入文本"""
        try:
            import requests
            url = f"{self.base_url}/pipeline/feature-extraction/{self.model}"

            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                json={"inputs": texts}
            )
            response.raise_for_status()

            embeddings = response.json()
            return embeddings
        except Exception as e:
            logger.error(f"Failed to embed texts with HuggingFace: {e}")
            return []

    def get_dimension(self) -> int:
        """获取嵌入向量维度"""
        # 常见HuggingFace模型的维度映射
        dimension_map = {
            "sentence-transformers/all-MiniLM-L6-v2": 384,
            "sentence-transformers/all-mpnet-base-v2": 768,
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": 384,
        }
        return dimension_map.get(self.model, 768)

    async def close(self):
        """关闭HuggingFace客户端"""
        if hasattr(self, 'session'):
            self.session.close()
        logger.info("HuggingFace embedding client closed")


class EmbeddingFactory:
    """嵌入模型工厂类"""

    @staticmethod
    def create_embedding(config: Dict[str, Any]) -> EmbeddingInterface:
        """根据配置创建对应的嵌入模型实例"""
        provider = config.get("provider", EmbeddingProvider.LOCAL)

        if provider == EmbeddingProvider.LOCAL:
            return LocalEmbeddingAdapter(config)
        elif provider == EmbeddingProvider.OPENAI:
            return OpenAIEmbeddingAdapter(config)
        elif provider == EmbeddingProvider.AZURE:
            return AzureEmbeddingAdapter(config)
        elif provider == EmbeddingProvider.HUGGINGFACE:
            return HuggingFaceEmbeddingAdapter(config)
        else:
            raise ValueError(f"Unsupported embedding provider: {provider}")

    @staticmethod
    def get_supported_providers() -> List[Dict[str, Any]]:
        """获取支持的嵌入模型提供商列表"""
        return [
            {
                "provider": EmbeddingProvider.LOCAL,
                "name": "本地模型",
                "description": "使用SentenceTransformers本地运行",
                "requires_api_key": False,
                "default_models": [
                    "all-MiniLM-L6-v2",
                    "all-mpnet-base-v2",
                    "paraphrase-multilingual-MiniLM-L12-v2",
                    "distiluse-base-multilingual-cased"
                ]
            },
            {
                "provider": EmbeddingProvider.OPENAI,
                "name": "OpenAI",
                "description": "OpenAI官方嵌入模型服务",
                "requires_api_key": True,
                "default_models": [
                    "text-embedding-ada-002",
                    "text-embedding-3-small",
                    "text-embedding-3-large"
                ]
            },
            {
                "provider": EmbeddingProvider.AZURE,
                "name": "Azure OpenAI",
                "description": "Azure OpenAI嵌入模型服务",
                "requires_api_key": True,
                "default_models": [
                    "text-embedding-ada-002",
                    "text-embedding-3-small",
                    "text-embedding-3-large"
                ]
            },
            {
                "provider": EmbeddingProvider.HUGGINGFACE,
                "name": "HuggingFace",
                "description": "HuggingFace推理API",
                "requires_api_key": True,
                "default_models": [
                    "sentence-transformers/all-MiniLM-L6-v2",
                    "sentence-transformers/all-mpnet-base-v2",
                    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
                ]
            }
        ]