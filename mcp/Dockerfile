# 阶段 1: 构建器 (Builder)
# 使用一个轻量级的 Python 镜像作为构建环境
FROM python:3.12-slim-bookworm AS builder

# 设置工作目录
WORKDIR /app

# 安装 uv，这是我们现代化的 Python 包管理器
# 我们使用 curl 从官方源获取安装脚本并执行
RUN apt-get update && apt-get install -y curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    apt-get remove -y curl && apt-get clean

# 将 uv 添加到 PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# 创建一个虚拟环境，这是最佳实践，可以隔离依赖
RUN uv venv /opt/venv

# 将 pyproject.toml 复制到工作目录
# 我们只复制这一个文件，以便利用 Docker 的层缓存机制
# 只有当这个文件改变时，依赖安装步骤才会重新运行
COPY pyproject.toml .

# 使用 uv 同步依赖项到虚拟环境中
# --no-cache 确保我们获得最新的包，避免缓存问题
RUN /opt/venv/bin/uv pip sync pyproject.toml --no-cache

# 阶段 2: 最终运行时 (Final Runtime)
# 使用与构建器相同的基础镜像，以确保兼容性
FROM python:3.12-slim-bookworm

# 创建一个非 root 用户来运行应用，增强安全性
# --no-create-home: 我们不需要为这个用户创建家目录
# --shell /bin/false: 出于安全考虑，禁止该用户登录 shell
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup --no-create-home --shell /bin/false appuser

# 设置工作目录
WORKDIR /app

# 从构建器阶段复制虚拟环境
# 这样我们的最终镜像就包含了所有预先安装好的依赖
COPY --from=builder /opt/venv /opt/venv

# 复制应用程序源代码
COPY . .

# 更改文件所有权为我们创建的非 root 用户
# 这是一个重要的安全步骤
RUN chown -R appuser:appgroup /app /opt/venv

# 切换到非 root 用户
USER appuser

# 设置 PATH，以便可以直接调用虚拟环境中的可执行文件
ENV PATH="/opt/venv/bin:${PATH}"

# 设置容器的入口点
# 当容器启动时，将执行此命令
CMD ["python", "main.py"]