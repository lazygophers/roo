"""
分层知识库API路由
支持知识库、文件夹、文件的层级管理
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.knowledge.core.hierarchical_service import get_hierarchical_knowledge_base_service
from app.knowledge.core.vector_interface import VectorDatabaseFactory
from app.knowledge.models.base import (
    KnowledgeBase, KnowledgeFolder, KnowledgeFile,
    CreateKnowledgeBaseRequest, UpdateKnowledgeBaseRequest,
    CreateFolderRequest, AddFileRequest,
    SearchRequest, SearchResult, KnowledgeBaseStats, FolderStats,
    FolderType, FileType, ProcessStatus
)
from app.core.logging import setup_logging

logger = setup_logging()
router = APIRouter()


@router.get("/test")
async def test_service():
    """测试分层知识库服务状态"""
    try:
        service = get_hierarchical_knowledge_base_service()
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "service_initialized": service is not None,
                    "database_path": service.db_path if service else None,
                    "model_loaded": service.model is not None if service else False
                }
            }
        )
    except Exception as e:
        logger.error(f"Knowledge base service test failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )


@router.get("/vector-databases")
async def get_supported_vector_databases():
    """获取支持的向量数据库列表"""
    try:
        databases = VectorDatabaseFactory.get_supported_databases()
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": databases
            }
        )
    except Exception as e:
        logger.error(f"Failed to get supported vector databases: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)}
        )


# 知识库管理API
@router.post("/knowledge-bases", response_model=KnowledgeBase)
async def create_knowledge_base(request: CreateKnowledgeBaseRequest):
    """创建知识库"""
    try:
        service = get_hierarchical_knowledge_base_service()
        if not service.model:
            await service.initialize()

        kb = await service.create_knowledge_base(request)
        return kb
    except Exception as e:
        logger.error(f"Error creating knowledge base: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create knowledge base: {str(e)}"
        )


@router.get("/knowledge-bases", response_model=List[KnowledgeBase])
async def list_knowledge_bases():
    """获取所有知识库列表"""
    try:
        service = get_hierarchical_knowledge_base_service()
        if not service.model:
            await service.initialize()

        knowledge_bases = await service.list_knowledge_bases()
        return knowledge_bases
    except Exception as e:
        logger.error(f"Error listing knowledge bases: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list knowledge bases: {str(e)}"
        )


@router.get("/knowledge-bases/{kb_id}")
async def get_knowledge_base(kb_id: str):
    """获取特定知识库详情"""
    try:
        service = get_hierarchical_knowledge_base_service()
        if not service.model:
            await service.initialize()

        # 这里需要实现获取单个知识库的方法
        return JSONResponse(
            status_code=200,
            content={"success": True, "message": "Knowledge base details endpoint"}
        )
    except Exception as e:
        logger.error(f"Error getting knowledge base: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get knowledge base: {str(e)}"
        )


@router.put("/knowledge-bases/{kb_id}")
async def update_knowledge_base(kb_id: str, request: UpdateKnowledgeBaseRequest):
    """更新知识库"""
    try:
        service = get_hierarchical_knowledge_base_service()
        if not service.model:
            await service.initialize()

        # 这里需要实现更新知识库的方法
        return JSONResponse(
            status_code=200,
            content={"success": True, "message": "Knowledge base updated"}
        )
    except Exception as e:
        logger.error(f"Error updating knowledge base: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update knowledge base: {str(e)}"
        )


@router.delete("/knowledge-bases/{kb_id}")
async def delete_knowledge_base(kb_id: str):
    """删除知识库"""
    try:
        service = get_hierarchical_knowledge_base_service()
        if not service.model:
            await service.initialize()

        # 这里需要实现删除知识库的方法
        return JSONResponse(
            status_code=200,
            content={"success": True, "message": "Knowledge base deleted"}
        )
    except Exception as e:
        logger.error(f"Error deleting knowledge base: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete knowledge base: {str(e)}"
        )


# 文件夹管理API
@router.post("/folders", response_model=KnowledgeFolder)
async def create_folder(request: CreateFolderRequest):
    """创建文件夹"""
    try:
        service = get_hierarchical_knowledge_base_service()
        if not service.model:
            await service.initialize()

        folder = await service.create_folder(request)
        return folder
    except Exception as e:
        logger.error(f"Error creating folder: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create folder: {str(e)}"
        )


@router.get("/folders")
async def list_folders(
    knowledge_base_id: Optional[str] = None,
    parent_folder_id: Optional[str] = None
):
    """获取文件夹列表"""
    try:
        service = get_hierarchical_knowledge_base_service()
        if not service.model:
            await service.initialize()

        # 这里需要实现获取文件夹列表的方法
        return JSONResponse(
            status_code=200,
            content={"success": True, "data": [], "message": "Folders list endpoint"}
        )
    except Exception as e:
        logger.error(f"Error listing folders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list folders: {str(e)}"
        )


@router.get("/folders/{folder_id}")
async def get_folder(folder_id: str):
    """获取文件夹详情"""
    try:
        service = get_hierarchical_knowledge_base_service()
        if not service.model:
            await service.initialize()

        # 这里需要实现获取单个文件夹的方法
        return JSONResponse(
            status_code=200,
            content={"success": True, "message": "Folder details endpoint"}
        )
    except Exception as e:
        logger.error(f"Error getting folder: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get folder: {str(e)}"
        )


@router.delete("/folders/{folder_id}")
async def delete_folder(folder_id: str):
    """删除文件夹"""
    try:
        service = get_hierarchical_knowledge_base_service()
        if not service.model:
            await service.initialize()

        # 这里需要实现删除文件夹的方法
        return JSONResponse(
            status_code=200,
            content={"success": True, "message": "Folder deleted"}
        )
    except Exception as e:
        logger.error(f"Error deleting folder: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete folder: {str(e)}"
        )


# 文件管理API
@router.post("/files", response_model=KnowledgeFile)
async def add_file(request: AddFileRequest):
    """添加文件"""
    try:
        service = get_hierarchical_knowledge_base_service()
        if not service.model:
            await service.initialize()

        file = await service.add_file(request)
        return file
    except Exception as e:
        logger.error(f"Error adding file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add file: {str(e)}"
        )


@router.get("/files")
async def list_files(
    knowledge_base_id: Optional[str] = None,
    folder_id: Optional[str] = None,
    file_type: Optional[FileType] = None
):
    """获取文件列表"""
    try:
        service = get_hierarchical_knowledge_base_service()
        if not service.model:
            await service.initialize()

        # 这里需要实现获取文件列表的方法
        return JSONResponse(
            status_code=200,
            content={"success": True, "data": [], "message": "Files list endpoint"}
        )
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list files: {str(e)}"
        )


@router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """删除文件"""
    try:
        service = get_hierarchical_knowledge_base_service()
        if not service.model:
            await service.initialize()

        # 这里需要实现删除文件的方法
        return JSONResponse(
            status_code=200,
            content={"success": True, "message": "File deleted"}
        )
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )


# 搜索API
@router.post("/search", response_model=List[SearchResult])
async def search_knowledge_base(request: SearchRequest):
    """搜索知识库"""
    try:
        service = get_hierarchical_knowledge_base_service()
        if not service.model:
            await service.initialize()

        results = await service.search_documents(request)
        return results
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search knowledge base: {str(e)}"
        )


# 统计信息API
@router.get("/stats")
async def get_stats():
    """获取总体统计信息"""
    try:
        service = get_hierarchical_knowledge_base_service()
        if not service.model:
            await service.initialize()

        # 这里需要实现获取统计信息的方法
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "total_knowledge_bases": 0,
                    "total_folders": 0,
                    "total_files": 0,
                    "total_chunks": 0,
                    "total_size_bytes": 0,
                    "total_size_mb": 0.0
                },
                "message": "Stats endpoint"
            }
        )
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.get("/stats/knowledge-base/{kb_id}")
async def get_knowledge_base_stats(kb_id: str):
    """获取特定知识库的统计信息"""
    try:
        service = get_hierarchical_knowledge_base_service()
        if not service.model:
            await service.initialize()

        # 这里需要实现获取知识库统计的方法
        return JSONResponse(
            status_code=200,
            content={"success": True, "message": "Knowledge base stats endpoint"}
        )
    except Exception as e:
        logger.error(f"Error getting knowledge base stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get knowledge base stats: {str(e)}"
        )


# 支持的格式API
@router.get("/supported-formats")
async def get_supported_formats():
    """获取支持的格式列表"""
    try:
        folder_types = {
            "local": "本地文件夹 - 扫描本地目录中的文档",
            "website": "网站链接 - 抓取网页内容",
            "github": "GitHub仓库 - 同步GitHub仓库内容",
            "cloud": "云存储 - 连接云存储服务",
            "virtual": "虚拟文件夹 - 用于组织和分类"
        }

        file_types = {
            "document": "文档文件 - PDF、DOC、TXT、MD等",
            "webpage": "网页内容 - HTML网页",
            "repository": "代码仓库 - GitHub仓库文件",
            "note": "笔记 - 个人笔记和备忘",
            "bookmark": "书签 - 网页书签链接"
        }

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "folder_types": folder_types,
                    "file_types": file_types,
                    "supported_extensions": [".txt", ".md", ".pdf", ".doc", ".docx", ".html"]
                }
            }
        )
    except Exception as e:
        logger.error(f"Error getting supported formats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get supported formats: {str(e)}"
        )