import atexit
import os.path
import threading
import time

from tinydb import TinyDB, Query

from pydantic import Field, BaseModel

from core.cache import mkdir
from core.croe import mcp


class Task(BaseModel):
    namespace: str = Field(
        description="命名空间",
        examples=["github.com/lazygophers/utils", "github.com/lazygophers/log"],
    )
    task_id: str = Field(
        description="任务ID, namespace下唯一",
        examples=["go-code-add-1", "pyton-test-add-1"],
    )
    name: str = Field(description="任务名称", examples=["为 add 函数添加测试"])
    desc: str = Field(
        description="任务描述",
        default=None,
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
        default=None,
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
    )
    started_at: int = Field(
        description="任务开始时间",
    )
    finished_at: int = Field(
        description="任务完成时间",
    )

    perent_task_id: str = Field(
        description="父任务ID",
        default=None,
    )

    def merge(self, task: dict):
        if task is None:
            return

        if task.name is not None:
            self.name = task.name

        if task.desc is not None:
            self.desc = task.desc

        if task.task_type is not None:
            self.task_type = task.task_type

        if task.priority is not None:
            self.priority = task.priority

        if task.status is not None:
            self.status = task.status

        if task.perent_task_id is not None:
            self.perent_task_id = task.perent_task_id

        if task.created_at is not None:
            self.created_at = task.created_at

        if task.started_at is not None:
            self.started_at = task.started_at

        if task.finished_at is not None:
            self.finished_at = task.finished_at

        if task.updated_at is not None:
            self.updated_at = task.updated_at

        if task.updated_at is not None:
            self.updated_at = task.updated_at

        if task.updated_at is not None:
            self.updated_at = task.updated_at

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
            "perent_task_id": self.perent_task_id,
        }


class TaskManager(object):
    def __init__(self):
        self.lock = threading.Lock()
        filename = os.path.join("cache", "task", "manager.json")
        mkdir(os.path.dirname(filename))
        self.db = TinyDB(filename)
        atexit.register(self.db.close)

    def add(self, task: Task) -> bool:
        task.created_at = int(time.time())
        task.status = "todo"

        with self.lock:
            table = self.db.table(task.namespace)
            if table.search(Query().task_id == task.task_id).__len__() > 0:
                return False
            table.insert(task.dict())
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
            table = self.db.table(namespace)
            table.remove()
            return True

    def update(self, task: Task) -> bool:
        with self.lock:
            table = self.db.table(task.namespace)
            table.update(
                task.dict(),
                Query().task_id == task.task_id,
            )
            return True


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
        default=None,
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
        default=None,
    ),
    priority: int = Field(
        description="任务优先级",
        examples=[1, 2, 3, 4, 5],
        default=3,
    ),
    perent_task_id: str = Field(
        description="父任务ID",
        default=None,
    ),
) -> bool:
    """
    添加一个任务
    """

    manager.add(Task(**locals()))


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
    return manager.list(namespace)


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
    task_id: str = Field(
        description="任务ID, namespace下唯一",
        examples=["go-code-add-1", "pyton-test-add-1,"],
    ),
    name: str = Field(description="任务名称", examples=["为 add 函数添加测试"]),
    desc: str = Field(
        description="任务描述",
        default=None,
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
        default=None,
    ),
    priority: int = Field(
        description="任务优先级",
        examples=[1, 2, 3, 4, 5],
        default=3,
    ),
    status: str = Field(
        description="任务状态",
        examples=["todo", "doing", "done", "retry"],
        default="todo",
    ),
    created_at: int = Field(
        description="任务创建时间",
    ),
    started_at: int = Field(
        description="任务开始时间",
    ),
    finished_at: int = Field(
        description="任务完成时间",
    ),
    perent_task_id: str = Field(
        description="父任务ID",
        default=None,
    ),
):
    """
    更新一个任务
    """
    return manager.update(Task(**locals()))


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
    manager.update(task)


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
    manager.update(task)
