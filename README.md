# 电商销售与库存智能分析平台

本项目是一个面向“大数据与云计算”课程设计的前后端分离系统，使用 Docker Compose 编排前端、后端、openGauss 和 Spark 伪分布式运行环境。

## 服务组成

`docker-compose.yml` 启动 5 个服务：

| 服务 | 容器名 | 镜像/构建方式 | 端口 |
| --- | --- | --- | --- |
| `opengauss` | `ecommerce-opengauss` | `opengauss/opengauss-server:latest` | `5432:5432` |
| `spark-master` | `ecommerce-spark-master` | `spark:3.5.6-scala2.12-java17-python3-ubuntu` | `7077:7077`、`8082:8080` |
| `spark-worker` | `ecommerce-spark-worker` | `spark:3.5.6-scala2.12-java17-python3-ubuntu` | `8083:8081` |
| `backend` | `ecommerce-backend` | 从 `./backend` 构建，镜像名 `cloud-compute-backend` | `${BACKEND_PORT:-8000}:8000` |
| `frontend` | `ecommerce-frontend` | 从 `./frontend` 构建，镜像名 `cloud-compute-frontend` | `${FRONTEND_PORT:-8080}:80` |

openGauss 数据保存在 Docker volume `opengauss_data` 中。后端会等待 openGauss 健康检查通过后再启动，并通过 `spark://spark-master:7077` 提交 Spark 分析任务。

`backend` 和 `frontend` 服务同时配置了 `image` 与 `build`：

- 执行 `docker compose build` 时，会从源码目录构建镜像，并写入固定镜像名 `cloud-compute-backend:latest` 和 `cloud-compute-frontend:latest`。
- 只执行 `docker compose up -d` 时，Compose 会直接使用本地已有的上述镜像；如果镜像来自 `cloud-compute.tar`，则不需要保留前后端源码目录。

## 环境要求

- Docker
- Docker Compose v2
- 能访问 Docker Hub 或已准备好 `cloud-compute.tar`

首次部署前复制环境变量文件：

```bash
test -f .env || cp .env.example .env
```

常用变量：

```env
OPENGAUSS_DATABASE=postgres
OPENGAUSS_USER=appuser
OPENGAUSS_PASSWORD=AppUser@123
BACKEND_PORT=8000
FRONTEND_PORT=8080
```

如需修改数据库密码、数据库名、后端端口或前端端口，修改 `.env` 后重新启动 Compose。

## 部署方式一：源码构建并启动

适用于保留完整源码目录，或希望从当前源码重新构建前后端镜像的场景。

需要的文件和目录：

```bash
docker-compose.yml
.env
backend/
frontend/
```

```bash
test -f .env || cp .env.example .env
docker compose build
docker compose up -d
```

也可以合并为一条命令：

```bash
docker compose up --build -d
```

源码构建完成后，会得到并使用以下业务镜像：

```bash
cloud-compute-backend:latest
cloud-compute-frontend:latest
```

如果本地没有 openGauss 或 Spark 镜像，`docker compose up -d` 会按 `docker-compose.yml` 自动拉取：

```bash
opengauss/opengauss-server:latest
spark:3.5.6-scala2.12-java17-python3-ubuntu
```

如需显式拉取第三方镜像，可先执行：

```bash
docker compose pull opengauss spark-master spark-worker
```

## 部署方式二：使用 cloud-compute.tar 导入镜像并启动

适用于离线环境、服务器网络不稳定的场景。

这种方式不需要保留前端、后端源码目录。

需要的文件：

```bash
docker-compose.yml
.env
cloud-compute.tar
```

将 `cloud-compute.tar` 放到与 `docker-compose.yml` 相同的目录后执行：

```bash
test -f .env || cp .env.example .env
docker load -i cloud-compute.tar
docker compose up -d
```

不要在这种方式下执行 `docker compose build` 或 `docker compose up --build`，否则 Compose 会尝试读取 `./backend` 和 `./frontend` 源码目录重新构建镜像。

`cloud-compute.tar` 应至少包含以下镜像：

```bash
cloud-compute-backend
cloud-compute-frontend
opengauss/opengauss-server:latest
spark:3.5.6-scala2.12-java17-python3-ubuntu
```

可用下面的命令检查当前 Compose 需要的镜像名：

```bash
docker compose config --images
```

## 访问地址

服务启动后访问：

- 前端：http://localhost:8080
- 后端 API 文档：http://localhost:8000/docs
- Spark Master UI：http://localhost:8082
- Spark Worker UI：http://localhost:8083

如果在 `.env` 中修改了 `FRONTEND_PORT` 或 `BACKEND_PORT`，以实际配置的端口为准。

首次打开前端后，在“分析任务”页面点击“初始化模拟数据”，再点击“运行 Spark 分析”。

## 常用运维命令

查看服务状态：

```bash
docker compose ps
```

查看日志：

```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f opengauss
```

重启服务：

```bash
docker compose restart
```

停止服务：

```bash
docker compose down
```

停止服务并删除 openGauss 数据卷：

```bash
docker compose down -v
```

## 验证命令

```bash
docker compose config
docker compose config --images
docker compose ps
```

前端和后端镜像也可以单独构建验证：

```bash
docker compose build backend frontend
```
