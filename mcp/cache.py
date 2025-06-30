import atexit
import os.path
import shelve
import threading
import time


def mkdir(dir_path: str):
    if dir_path == "":
        return
    mkdir(os.path.dirname(dir_path))
    if os.path.exists(dir_path):
        return
    os.mkdir(dir_path)


class Cache:
    def __init__(self, filename: str):
        self.filename = filename
        self.lock = threading.Lock()
        self.db = None
        self.open()

    def open(self):
        """打开数据库"""
        mkdir(os.path.dirname(self.filename))

        self.db = shelve.open(self.filename, writeback=True)
        atexit.register(self.close)

    def close(self):
        """关闭数据库"""
        if self.db:
            self.db.close()

    def get(self, key):
        """获取键值（支持 TTL 检查）"""
        with self.lock:
            if self.db is None:
                raise RuntimeError("Database not opened")
            if key in self.db:
                value, expire_time = self.db[key]
                if time.time() < expire_time:
                    return value
                else:
                    # 键已过期，删除
                    del self.db[key]

        self._cleanup_expired()
        return None

    def set(self, key, value, ttl=0):
        """
        设置键值（支持 TTL）
        :param key: 键
        :param value: 值
        :param ttl: 超时时间（秒），0 表示永不过期
        """
        with self.lock:
            if self.db is None:
                raise RuntimeError("Database not opened")
            expire_time = time.time() + ttl if ttl > 0 else float("inf")
            self.db[key] = (value, expire_time)

        self._cleanup_expired()

    def delete(self, key):
        """删除键"""
        with self.lock:
            if self.db is None:
                raise RuntimeError("Database not opened")
            if key in self.db:
                del self.db[key]

    def clear(self):
        """清空数据库"""
        with self.lock:
            if self.db is None:
                raise RuntimeError("Database not opened")
            self.db.clear()

    def exists(self, key) -> bool:
        """检查键是否存在"""
        with self.lock:
            if self.db is None:
                raise RuntimeError("Database not opened")
            return key in self.db

    def _cleanup_expired(self):
        with self.lock:
            now = time.time()
            for key in list(self.db.keys()):
                _, expire_time = self.db[key]
                if now >= expire_time:
                    del self.db[key]

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 示例用法
if __name__ == "__main__":
    db = Cache("my_kvdb.db")
    db.open()

    # 设置带 TTL 的键值
    db.set("key1", "value1", ttl=5)  # 5秒后过期
    db.set("key2", "value2")  # 永不过期

    # 获取值
    print(db.get("key1"))  # 输出: value1
    time.sleep(6)  # 等待 key1 过期
    print(db.get("key1"))  # 输出: None
    print(db.get("key2"))  # 输出: value2

    db.close()