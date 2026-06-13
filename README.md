# 电商销售与库存智能分析平台

这是一个面向“大数据与云计算”课程设计的前后端分离项目，使用 Spark + openGauss，并通过 Docker Compose 部署伪分布式服务。

## 技术栈

- 前端：Vue 3、Vite、ECharts、Nginx
- 后端：FastAPI、SQLAlchemy、psycopg、PySpark
- 数据库：openGauss 官方镜像 `opengauss/opengauss-server:7.0.0-RC3.B016`
- 大数据处理：Docker Official Image `spark:3.5.6-scala2.12-java17-python3-ubuntu`
- 容器化：Docker Compose

## 启动

```bash
cp .env.example .env
docker compose pull
docker compose up --build
```

如果本地访问 Docker Hub 不稳定导致 `docker compose pull` 超时，直接重试该命令即可；Compose 中的第三方服务仍然使用固定官方镜像名，不需要改成本地已有镜像。

访问地址：

- 前端：http://localhost:8080
- 后端 API：http://localhost:8000/docs
- Spark Master UI：http://localhost:8082
- Spark Worker UI：http://localhost:8083

首次打开前端后，在“分析任务”页面点击“初始化模拟数据”，再点击“运行 Spark 分析”。

## 官方镜像约束

本项目不依赖本地已有镜像：

- openGauss 和 Spark 直接从官方公开镜像源拉取。
- 后端镜像基于官方 `python:3.12-slim-bookworm` 构建。
- 前端构建阶段基于官方 `node:22-alpine`，运行阶段基于官方 `nginx:1.27-alpine`。
- Compose 不使用 `latest`，便于本地 ARM 与华为云 x86 环境复现。

## 业务功能

- 商品管理：新增、编辑、删除、搜索、库存调整。
- 订单管理：订单列表、订单明细、状态筛选。
- 运营看板：销售额、订单数、库存预警、销售趋势、热销商品、分类占比。
- 分析任务：初始化模拟数据、触发 Spark 批处理、查看分析运行记录。

## 上云迁移

在华为云 x86 服务器上安装 Docker 与 Docker Compose 后，拉取源码并执行：

```bash
cp .env.example .env
docker compose pull
docker compose up --build -d
```

如需修改端口、数据库密码或 Spark 参数，只改 `.env`，不要改镜像名。

## 验证命令

```bash
docker compose config
docker compose config --images
docker compose build backend frontend
npm --prefix frontend run build
npm --prefix frontend audit --omit=dev
```
