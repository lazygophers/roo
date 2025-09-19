from fastapi import APIRouter
from .api_models import router as models_router
from .api_hooks import router as hooks_router
from .api_rules import router as rules_router
from .api_commands import router as commands_router
from .api_database import router as database_router
from .api_configurations import router as configurations_router
from .api_roles import router as roles_router
from .api_deploy import router as deploy_router
from .api_system_monitor import router as system_monitor_router
from .api_file_security import router as file_security_router
from .api_recycle_bin import router as recycle_bin_router
from .api_time_tools import router as time_tools_router
from .api_cache_tools import router as cache_tools_router
from .api_cache import router as cache_router
from .mcp import router as mcp_router
from .api_mcp_config import router as mcp_config_router
from .api_web_scraping import router as web_scraping_router
from .api_knowledge_base import router as knowledge_base_router

# 创建主路由
api_router = APIRouter()

# 注册子路由
api_router.include_router(models_router, tags=["models"])
api_router.include_router(hooks_router, tags=["hooks"])
api_router.include_router(rules_router, tags=["rules"])
api_router.include_router(commands_router, tags=["commands"])
api_router.include_router(database_router, tags=["database"])
api_router.include_router(configurations_router, tags=["configurations"])
api_router.include_router(roles_router, tags=["roles"])
api_router.include_router(deploy_router, prefix="/deploy", tags=["deploy"])
api_router.include_router(system_monitor_router, tags=["system"])
api_router.include_router(file_security_router, tags=["file-security"])
api_router.include_router(recycle_bin_router, tags=["recycle-bin"])
api_router.include_router(time_tools_router, tags=["time-tools"])
api_router.include_router(cache_tools_router, tags=["cache-tools"])
api_router.include_router(cache_router, tags=["cache"])
api_router.include_router(mcp_router, tags=["mcp"])
api_router.include_router(mcp_config_router, tags=["mcp-config"])
api_router.include_router(web_scraping_router, tags=["web-scraping"])
api_router.include_router(knowledge_base_router, prefix="/knowledge-base", tags=["knowledge-base"])