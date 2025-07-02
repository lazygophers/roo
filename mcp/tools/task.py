import atexit
import os.path
import threading
import time
from typing import Mapping

from tinydb import TinyDB, Query

from pydantic import Field, BaseModel

from core.cache import mkdir
from core.croe import mcp


class Task(BaseModel, Query, Mapping):
    def __len__(self):
        return len(self.dict().keys())

    task_id: str = Field(
        description="任务ID, namespace下唯一",
        examples=["go-code-add-1", "pyton-test-add-1"],
    )
    name: str = Field(description="任务名称", examples=["为 add 函数添加测试"])
    desc: str = Field(
        description="任务描述",
        default="",
    )
    task_type: str = Field(
        description="任务类型",
        examples=[
            "add",
            "test",
            "fix",
            "doc",
            "refactor",
            "style",
            "perf",
            "ci",
            "chore",
        ],
        default="",
    )
    priority: int = Field(
        description="任务优先级",
        examples=[1, 2, 3, 4, 5],
        default=3,
    )

    status: str = Field(
        description="任务状态",
        examples=["todo", "doing", "done", "retry"],
        default="todo",
    )

    created_at: int = Field(
        description="任务创建时间",
        default=0,
    )
    started_at: int = Field(
        description="任务开始时间",
        default=0,
    )
    finished_at: int = Field(
        description="任务完成时间",
        default=0,
    )

    parent_task_id: str = Field(
        description="父任务ID",
        default=0,
    )

    order: int = Field(
        description="任务排序",
        default=0,
    )

    def dict(self):
        return {
            "task_id": self.task_id,
            "name": self.name,
            "desc": self.desc,
            "task_type": self.task_type,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "parent_task_id": self.parent_task_id,
            "order": self.order,
        }


class TaskManager(object):
    def __init__(self):
        self.lock = threading.Lock()
        filename = os.path.join("cache", "task", "manager.json")
        mkdir(os.path.dirname(filename))
        self.db = TinyDB(filename)
        atexit.register(self.db.close)

    def add(self, namespace: str, task: Task) -> bool:
        task.created_at = int(time.time())
        task.status = "todo"

        with self.lock:
            table = self.db.table(namespace)
            if table.contains(Query().task_id == task.task_id):
                return False
            table.insert(task.dict())
            return True

    def replace(self, namespace: str, tasks: list[Task]) -> bool:
        for task in tasks:
            task.created_at = int(time.time())

        with self.lock:
            table = self.db.table(namespace)
            table.truncate()
            table.insert_multiple([task.dict() for task in tasks])
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
                task.dict(),
                Query().task_id == task.task_id,
            )
            return True

    def exists(self, namespace: str, task_id: str) -> bool:
        with self.lock:
            table = self.db.table(namespace)
            return table.contains(Query().task_id == task_id)


manager = TaskManager()


@mcp.tool()
async def task_add(
    namespace: str = Field(
        description="命名空间",
        examples=["github.com/lazygophers/utils", "github.com/lazygophers/log"],
    ),
    task_id: str = Field(
        description="任务ID, namespace下唯一",
        examples=["go-code-add-1", "pyton-test-add-1"],
    ),
    name: str = Field(description="任务名称", examples=["为 add 函数添加测试"]),
    desc: str = Field(
        description="任务描述",
        default="",
    ),
    task_type: str = Field(
        description="任务类型",
        examples=[
            "add",
            "test",
            "fix",
            "doc",
            "refactor",
            "style",
            "perf",
            "ci",
            "chore",
        ],
    ),
    priority: int = Field(
        description="任务优先级",
        examples=[1, 2, 3, 4, 5],
        default=3,
    ),
    parent_task_id: str = Field(
        description="父任务ID",
        default="",
    ),
    order: int = Field(
        description="任务排序",
        default=0,
    ),
) -> bool:
    """
    添加一个任务
    """

    return manager.add(
        namespace,
        Task(
            task_id=task_id,
            name=name,
            desc=desc,
            task_type=task_type,
            priority=priority,
            parent_task_id=parent_task_id,
            order=order,
        ),
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
        examples=["todo", "doing", "done", "retry"],
    ),
):
    """
    任务开始
    """
    task = manager.get(namespace, task_id)
    task.started_at = int(time.time())
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
        examples=["todo", "doing", "done", "retry"],
    ),
):
    """
    任务完成
    """
    task = manager.get(namespace, task_id)
    task.finished_at = int(time.time())
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