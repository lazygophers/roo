# -*- coding: utf-8 -*-
"""
@author: lancelrq
@description: 数据库核心服务，封装与 LanceDB 和 DuckDB 的所有交互。
"""

import logging
from pathlib import Path
from typing import Type, TypeVar

import lancedb
from lancedb.db import LanceDBConnection
from lancedb.table import LanceTable
from duckdb import DuckDBPyConnection

from src.config import get_config
from src.memory.models import CoreMemory, KnowledgeMemory, WorkingMemory, BaseMemory

# 定义一个类型变量，用于表示 BaseMemory 的子类
T = TypeVar("T", bound=BaseMemory)

class DatabaseService:
    """
    数据库服务类，负责管理与 LanceDB 的所有交互，包括连接、
    表创建、数据增删改查以及 DuckDB 查询。
    """

    def __init__(self):
        """
        初始化数据库服务。

        - 连接到 LanceDB 数据库。
        - 为 CoreMemory, KnowledgeMemory, WorkingMemory 模型创建或打开表。
        """
        self.config = get_config().memory
        self.db_path = Path(self.config.db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.db: LanceDBConnection = lancedb.connect(str(self.db_path))
        
        # 为每个模型创建或打开表
        self.core_table: LanceTable = self._get_or_create_table("CoreMemory", CoreMemory)
        self.knowledge_table: LanceTable = self._get_or_create_table("KnowledgeMemory", KnowledgeMemory)
        self.working_table: LanceTable = self._get_or_create_table("WorkingMemory", WorkingMemory)

        self._init_status_table()

        logging.info(f"数据库服务初始化完成，连接到: {self.db_path}")

    def _get_or_create_table(self, table_name: str, schema: Type[T]) -> LanceTable:
        """
        获取或创建指定名称和模式的 LanceDB 表。

        :param table_name: 表的名称。
        :param schema: 表的 Pydantic 模型（继承自 LanceModel）。
        :return: 返回一个 LanceTable 实例。
        """
        try:
            if table_name in self.db.table_names():
                logging.debug(f"打开已存在的表: {table_name}")
                return self.db.open_table(table_name)
            else:
                logging.info(f"创建新表: {table_name}")
                return self.db.create_table(table_name, schema=schema)
        except Exception as e:
            logging.error(f"获取或创建表 '{table_name}' 失败: {e}", exc_info=True)
            raise

    def add(self, data: T):
        """
        向数据库中添加一条新的记忆数据。

        根据传入数据的类型，动态选择对应的表进行写入。

        :param data: 继承自 BaseMemory 的 Pydantic 模型实例。
        """
        try:
            table = self._get_table_by_model(type(data))
            table.add([data])
            logging.info(f"成功向表 '{table.name}' 添加数据，ID: {data.id}")
        except Exception as e:
            logging.error(f"添加数据失败: {e}", exc_info=True)
            raise

    def get(self, model: Type[T], item_id: str) -> T | None:
        """
        根据 ID 从指定的表中检索一条记忆数据。

        :param model: 要查询的模型类型 (e.g., CoreMemory)。
        :param item_id: 要检索的数据的唯一 ID。
        :return: 返回 Pydantic 模型实例，如果未找到则返回 None。
        """
        try:
            table = self._get_table_by_model(model)
            result = table.search(query=item_id, query_type="sql").where(f"id = '{item_id}'").limit(1).to_pydantic()
            if result:
                logging.debug(f"从表 '{table.name}' 成功检索到数据，ID: {item_id}")
                return result[0]
            logging.warning(f"在表 '{table.name}' 中未找到 ID 为 '{item_id}' 的数据")
            return None
        except Exception as e:
            logging.error(f"检索数据失败: {e}", exc_info=True)
            raise

    def update(self, model: Type[T], item_id: str, updates: dict):
        """
        更新指定 ID 的记忆数据。

        注意：LanceDB 的 update 是一个重量级操作，因为它会重写数据文件。
        请谨慎使用，尤其是在频繁更新的场景下。

        :param model: 要更新的数据所属的模型类型。
        :param item_id: 要更新的数据的唯一 ID。
        :param updates: 一个包含待更新字段及其新值的字典。
        """
        try:
            table = self._get_table_by_model(model)
            table.update(where=f"id = '{item_id}'", values=updates)
            logging.info(f"成功更新表 '{table.name}' 中 ID 为 '{item_id}' 的数据")
        except Exception as e:
            logging.error(f"更新数据失败: {e}", exc_info=True)
            raise

    def delete(self, model: Type[T], item_id: str):
        """
        根据 ID 从指定的表中删除一条记忆数据。

        :param model: 要删除的数据所属的模型类型。
        :param item_id: 要删除的数据的唯一 ID。
        """
        try:
            table = self._get_table_by_model(model)
            table.delete(f"id = '{item_id}'")
            logging.info(f"成功从表 '{table.name}' 删除 ID 为 '{item_id}' 的数据")
        except Exception as e:
            logging.error(f"删除数据失败: {e}", exc_info=True)
            raise

    def query_duckdb(self, query: str) -> DuckDBPyConnection:
        """
        对 LanceDB 表执行 DuckDB SQL 查询。

        :param query: 要执行的 DuckDB SQL 查询语句。
        :return: 返回一个 DuckDB 查询结果连接对象。
        """
        try:
            return self.db.query(query)
        except Exception as e:
            logging.error(f"DuckDB 查询失败: {e}", exc_info=True)
            raise

    def _get_table_by_model(self, model: Type[T]) -> LanceTable:
        """
        根据模型类型返回对应的 LanceDB 表实例。

        :param model: 模型类型 (e.g., CoreMemory)。
        :return: 对应的 LanceTable 实例。
        :raises ValueError: 如果传入了未知的模型类型。
        """
        if model == CoreMemory:
            return self.core_table
        elif model == KnowledgeMemory:
            return self.knowledge_table
        elif model == WorkingMemory:
            return self.working_table
        else:
            raise ValueError(f"未知的模型类型: {model.__name__}")

    def _init_status_table(self):
        """
        初始化 DuckDB 中的 system_status 表。

        如果表不存在，则创建它。
        如果表中没有 'memory_status' 记录，则插入默认值 'ON'。
        """
        try:
            # 1. 创建 system_status 表（如果不存在）
            create_table_query = "CREATE TABLE IF NOT EXISTS system_status (key VARCHAR, value VARCHAR);"
            self.query_duckdb(create_table_query)
            logging.info("表 'system_status' 已确保存在。")

            # 2. 检查 'memory_status' 是否存在
            check_query = "SELECT value FROM system_status WHERE key = 'memory_status';"
            result = self.query_duckdb(check_query).fetchone()

            # 3. 如果不存在，则插入默认值
            if result is None:
                insert_query = "INSERT INTO system_status (key, value) VALUES ('memory_status', 'ON');"
                self.query_duckdb(insert_query)
                logging.info("默认状态 'memory_status' = 'ON' 已插入。")
            else:
                logging.debug(f"内存状态已存在: {result}")

        except Exception as e:
            logging.error(f"初始化 'system_status' 表失败: {e}", exc_info=True)
            raise

    def get_status(self) -> str:
        """
        查询当前的系统内存状态。

        :return: 返回状态字符串 (e.g., 'ON', 'OFF')。
        """
        try:
            query = "SELECT value FROM system_status WHERE key = 'memory_status';"
            result = self.query_duckdb(query).fetchone()
            if result:
                # fetchone() returns a tuple, e.g., ('ON',)
                status_value = result
                logging.debug(f"成功查询到内存状态: {status_value}")
                return status_value
            else:
                logging.error("未能在 'system_status' 表中找到 'memory_status' 记录。")
                return 'OFF'  # 返回一个安全的默认值
        except Exception as e:
            logging.error(f"查询内存状态失败: {e}", exc_info=True)
            return 'OFF'  # 发生异常时也返回默认值

    def set_status(self, new_status: str):
        """
        更新系统内存状态。

        :param new_status: 新的状态字符串。
        """
        try:
            # 使用 UPDATE ... FROM ... WHERE 语法，这是 DuckDB 中更新值的标准方式
            update_query = f"UPDATE system_status SET value = '{new_status}' WHERE key = 'memory_status';"
            self.query_duckdb(update_query)
            logging.info(f"成功将内存状态更新为: {new_status}")
        except Exception as e:
            logging.error(f"更新内存状态失败: {e}", exc_info=True)
            raise
