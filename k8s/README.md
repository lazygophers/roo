# LazyAI Studio Kubernetes 部署指南

本目录包含 LazyAI Studio 的完整 Kubernetes 配置文件，支持生产级别的容器化部署。

## 📁 文件结构

```
k8s/
├── namespace.yaml           # 命名空间定义
├── configmap.yaml          # 应用配置
├── persistent-volumes.yaml # 持久化存储
├── deployment.yaml         # 应用部署
├── service.yaml            # 服务暴露
├── ingress.yaml            # 入口控制器
├── hpa.yaml               # 水平扩缩容
├── kustomization.yaml     # Kustomize 配置
└── README.md              # 部署指南
```

## 🚀 快速部署

### 方法一：使用 kubectl 直接部署

```bash
# 1. 部署所有资源
kubectl apply -f k8s/

# 2. 检查部署状态
kubectl get pods -n lazyai-studio
kubectl get svc -n lazyai-studio
kubectl get ingress -n lazyai-studio
```

### 方法二：使用 Kustomize 部署

```bash
# 1. 使用 kustomize 部署
kubectl apply -k k8s/

# 2. 检查部署状态
kubectl get all -n lazyai-studio
```

## 📋 部署前准备

### 1. 构建镜像

确保已构建 LazyAI Studio 镜像：

```bash
# 构建镜像
docker build -t lazyai-studio:latest .

# 或使用 make 命令
make docker-build
```

### 2. 配置存储

如果使用云存储，请修改 `persistent-volumes.yaml` 中的存储类：

```yaml
# 示例：使用 AWS EBS
storageClassName: gp2

# 示例：使用 GCP Persistent Disk
storageClassName: standard

# 示例：使用 Azure Disk
storageClassName: managed-premium
```

### 3. 配置域名（可选）

修改 `ingress.yaml` 中的域名配置：

```yaml
spec:
  rules:
  - host: your-domain.com  # 修改为您的域名
```

## 🔧 配置说明

### 环境变量配置

在 `configmap.yaml` 中配置应用环境变量：

```yaml
data:
  ENVIRONMENT: "remote"      # 生产环境
  DEBUG: "false"             # 关闭调试
  LOG_LEVEL: "INFO"          # 日志级别
  CORS_ORIGINS: "https://your-domain.com"  # CORS 配置
```

### 资源限制

在 `deployment.yaml` 中调整资源配置：

```yaml
resources:
  requests:
    cpu: 50m      # 最小 CPU
    memory: 64Mi  # 最小内存
  limits:
    cpu: 250m     # 最大 CPU
    memory: 128Mi # 最大内存
```

### 扩缩容配置

在 `hpa.yaml` 中配置自动扩缩容：

```yaml
spec:
  minReplicas: 1    # 最小副本数
  maxReplicas: 3    # 最大副本数
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        averageUtilization: 70  # CPU 使用率阈值
```

## 🌐 访问方式

部署完成后，可通过以下方式访问：

### 1. NodePort 访问

```bash
# 获取节点 IP
kubectl get nodes -o wide

# 访问地址：http://<node-ip>:30800
```

### 2. Ingress 访问

```bash
# 配置 /etc/hosts 或 DNS
echo "$(kubectl get ingress -n lazyai-studio -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}') lazyai-studio.local" >> /etc/hosts

# 访问地址：http://lazyai-studio.local
```

### 3. 端口转发访问

```bash
# 端口转发
kubectl port-forward -n lazyai-studio svc/lazyai-studio-service 8000:8000

# 访问地址：http://localhost:8000
```

## 📊 监控和日志

### 查看 Pod 状态

```bash
kubectl get pods -n lazyai-studio -w
```

### 查看应用日志

```bash
kubectl logs -n lazyai-studio deployment/lazyai-studio -f
```

### 查看 Pod 详细信息

```bash
kubectl describe pod -n lazyai-studio <pod-name>
```

### 进入容器调试

```bash
kubectl exec -it -n lazyai-studio <pod-name> -- /bin/sh
```

## 🔄 更新部署

### 更新镜像

```bash
# 1. 构建新镜像
docker build -t lazyai-studio:v1.2.0 .

# 2. 更新部署
kubectl set image deployment/lazyai-studio -n lazyai-studio lazyai-studio=lazyai-studio:v1.2.0

# 3. 查看更新状态
kubectl rollout status deployment/lazyai-studio -n lazyai-studio
```

### 回滚部署

```bash
# 查看历史版本
kubectl rollout history deployment/lazyai-studio -n lazyai-studio

# 回滚到上一版本
kubectl rollout undo deployment/lazyai-studio -n lazyai-studio
```

## 🗑️ 清理资源

```bash
# 删除所有资源
kubectl delete -f k8s/

# 或使用 kustomize 删除
kubectl delete -k k8s/
```

## 🛠️ 故障排查

### 常见问题

1. **Pod 无法启动**
   ```bash
   kubectl describe pod -n lazyai-studio <pod-name>
   kubectl logs -n lazyai-studio <pod-name>
   ```

2. **存储卷无法挂载**
   ```bash
   kubectl get pv
   kubectl get pvc -n lazyai-studio
   ```

3. **服务无法访问**
   ```bash
   kubectl get svc -n lazyai-studio
   kubectl get endpoints -n lazyai-studio
   ```

4. **Ingress 配置问题**
   ```bash
   kubectl get ingress -n lazyai-studio
   kubectl describe ingress -n lazyai-studio lazyai-studio-ingress
   ```

## 📚 相关文档

- [Kubernetes 官方文档](https://kubernetes.io/docs/)
- [Kustomize 使用指南](https://kustomize.io/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)
- [Horizontal Pod Autoscaler](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)