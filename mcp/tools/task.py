import atexit
import os.path
import threading
from typing import Mapping

from pydantic import Field, BaseModel
from tinydb import TinyDB, Query

from core.cache import mkdir
from core.croe import mcp

task_state_examples = ["待执行", "执行中", "已完成", "已取消", "已失败", "等待重试"]
task_type_examples = [
    "搜索",
    "研究",
    "存储",
    "通知",
    "测试",
    "文档",
    "优化",
    "修复",
    "其他",
]


class Task(BaseModel, Query, Mapping):
    def __len__(self):
        return len(self.model_dump().keys())

    task_id: str = Field(
        description="任务ID, namespace下唯一",
        examples=["go-code-add-1", "pyton-test-add-1"],
    )
    name: str = Field(description="任务名称", examples=["为 add 函数添加测试"])
    desc: str = Field(
        description="任务描述",
        default="",
    )
    workflow: str = Field(
        description="任务工作流",
        default="",
    )

    task_type: str = Field(
        description="任务类型",
        examples=task_type_examples,
        default="其它",
    )
    priority: int = Field(
        description="任务优先级",
        examples=[1, 2, 3, 4, 5],
        default=3,
    )

    status: str = Field(
        description="任务状态",
        examples=task_state_examples,
        default=task_state_examples[0],
    )

    parent_task_id: str = Field(
        description="父任务ID",
        default=0,
    )

    order: int = Field(
        description="任务排序",
        default=0,
    )


class Manager(object):
    def __init__(self):
        self.lock = threading.Lock()
        filename = os.path.join("cache", "task", "manager.json")
        mkdir(os.path.dirname(filename))
        self.db = TinyDB(filename, encoding="utf-8")
        atexit.register(self.db.close)

    def add(self, namespace: str, task: Task) -> bool:
        task.status = task_state_examples[0]

        with self.lock:
            table = self.db.table(namespace)
            if table.contains(Query().task_id == task.task_id):
                return False
            table.insert(task.model_dump())
            return True

    def replace(self, namespace: str, tasks: list[Task]) -> bool:
        with self.lock:
            table = self.db.table(namespace)
            table.truncate()
            table.insert_multiple([task.model_dump() for task in tasks])
            return True

    def get(self, namespace: str, task_id: str) -> Task:
        with self.lock:
            table = self.db.table(namespace)
            task = table.search(Query().task_id == task_id)
            if task.__len__() > 0:
                return Task(**task[0])
            else:
                return None

    def list(self, namespace: str) -> list[Task]:
        with self.lock:
            table = self.db.table(namespace)
            tasks = table.all()
            return [Task(**task) for task in tasks]

    def delete(self, namespace: str, task_id: str) -> bool:
        with self.lock:
            table = self.db.table(namespace)
            table.remove(Query().task_id == task_id)
            return True

    def clear(self, namespace: str) -> bool:
        with self.lock:
            self.db.drop_table(namespace)
            return True

    def update(self, namespace: str, task: Task) -> bool:
        with self.lock:
            table = self.db.table(namespace)
            table.update(
                task.model_dump(),
                Query().task_id == task.task_id,
            )
            return True

    def exists(self, namespace: str, task_id: str) -> bool:
        with self.lock:
            table = self.db.table(namespace)
            return table.contains(Query().task_id == task_id)


manager = Manager()


@mcp.tool()
async def task_add(
    namespace: str = Field(
        description="命名空间",
        examples=["github.com/lazygophers/utils", "github.com/lazygophers/log"],
    ),
    task: Task = Field(description="任务"),
) -> bool:
    """
    添加一个任务
    """

    return manager.add(
        namespace,
        task,
    )


@mcp.tool()
async def task_replace(
    namespace: str = Field(
        description="命名空间",
        examples=["github.com/lazygophers/utils", "github.com/lazygophers/log"],
    ),
    tasks: list[Task] = Field(description="任务列表"),
):
    """
    替换命名空间下的所有任务
    """
    manager.replace(namespace, tasks)


@mcp.tool()
async def task_list(
    namespace: str = Field(
        description="命名空间",
        examples=["github.com/lazygophers/utils", "github.com/lazygophers/log"],
    ),
) -> list[Task]:
    """
    列出命名空间下的所有任务
    """
    tasks = manager.list(namespace)
    tasks.sort(key=lambda x: x.order)
    return tasks


@mcp.tool()
async def task_get(
    namespace: str = Field(
        description="命名空间",
        examples=["github.com/lazygophers/utils", "github.com/lazygophers/log"],
    ),
    task_id: str = Field(
        description="任务ID, namespace下唯一",
        examples=["go-code-add-1", "pyton-test-add-1"],
    ),
) -> Task:
    """
    获取一个任务
    """
    return manager.get(namespace, task_id)


@mcp.tool()
async def task_delete(
    namespace: str = Field(
        description="命名空间",
        examples=["github.com/lazygophers/utils", "github.com/lazygophers/log"],
    ),
    task_id: str = Field(
        description="任务ID, namespace下唯一",
        examples=["go-code-add-1", "pyton-test-add-1"],
    ),
) -> bool:
    """
    删除一个任务
    """
    return manager.delete(namespace, task_id)


@mcp.tool()
async def task_clear(
    namespace: str = Field(
        description="命名空间",
        examples=["github.com/lazygophers/utils", "github.com/lazygophers/log"],
    ),
) -> bool:
    """
    清空命名空间下的所有任务
    """
    return manager.clear(namespace)


@mcp.tool()
async def task_update(
    namespace: str = Field(
        description="命名空间",
        examples=["github.com/lazygophers/utils", "github.com/lazygophers/log"],
    ),
    task: Task = Field(description="任务"),
):
    """
    更新一个任务
    """
    return manager.update(namespace, task)


@mcp.tool()
async def task_start(
    namespace: str = Field(
        description="命名空间",
        examples=["github.com/lazygophers/utils", "github.com/lazygophers/log"],
    ),
    task_id: str = Field(
        description="任务ID, namespace下唯一",
        examples=["go-code-add-1", "pyton-test-add-1,"],
    ),
    status: str = Field(
        description="任务状态",
        examples=task_state_examples,
    ),
):
    """
    任务开始
    """
    task = manager.get(namespace, task_id)
    task.status = status
    manager.update(namespace, task)


@mcp.tool()
async def task_finish(
    namespace: str = Field(
        description="命名空间",
        examples=["github.com/lazygophers/utils", "github.com/lazygophers/log"],
    ),
    task_id: str = Field(
        description="任务ID, namespace下唯一",
        examples=["go-code-add-1", "pyton-test-add-1,"],
    ),
    status: str = Field(
        description="任务状态",
        examples=task_state_examples,
    ),
):
    """
    任务完成
    """
    task = manager.get(namespace, task_id)
    task.status = status
    manager.update(namespace, task)


@mcp.tool()
async def task_exist(
    namespace: str = Field(
        description="命名空间",
        examples=["github.com/lazygophers/utils", "github.com/lazygophers/log"],
    ),
    task_id: str = Field(
        description="任务ID, namespace下唯一",
    ),
) -> bool:
    """
    任务是否存在
    """
    return manager.exists(namespace, task_id)