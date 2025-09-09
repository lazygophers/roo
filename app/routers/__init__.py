from fastapi import APIRouter
from .api_models import router as models_router
from .api_hooks import router as hooks_router
from .api_rules import router as rules_router
from .api_commands import router as commands_router
from .api_database import router as database_router

# 创建主路由
api_router = APIRouter()

# 注册子路由
api_router.include_router(models_router, tags=["models"])
api_router.include_router(hooks_router, tags=["hooks"])
api_router.include_router(rules_router, tags=["rules"])
api_router.include_router(commands_router, tags=["commands"])
api_router.include_router(database_router, tags=["database"])