# 实验报告提纲

## 1. 实验目的

部署 openGauss 伪分布式数据库服务，开发并容器化一个前后端分离 Web 应用，使用 Spark 对 openGauss 中的电商订单数据进行批处理分析。

## 2. 系统架构

- 浏览器访问 Nginx 托管的 Vue 前端。
- Nginx 将 `/api` 代理到 FastAPI 后端。
- FastAPI 通过 psycopg/SQLAlchemy 读写 openGauss。
- FastAPI 触发 `spark-submit`，将 PySpark 作业提交到 Spark Standalone 集群。
- Spark 通过 openGauss JDBC 驱动读取订单数据并回写分析结果。

## 3. 容器服务

- `opengauss`：官方 openGauss 数据库镜像。
- `spark-master`：Spark Standalone master。
- `spark-worker`：Spark Standalone worker。
- `backend`：FastAPI 服务，从官方 Python 镜像构建。
- `frontend`：Vue 构建产物，由官方 Nginx 镜像托管。

## 4. 核心功能

- 商品 CRUD 与库存调整。
- 订单查询与订单明细查看。
- 模拟数据初始化。
- Spark 销售与库存分析。
- 看板图表展示：销售趋势、热销商品、分类销售额、库存预警。

## 5. 部署步骤

```bash
cp .env.example .env
docker compose pull
docker compose up --build -d
```

## 6. 测试记录

- 验证前端页面可以访问。
- 验证后端 `/docs` 可以访问。
- 初始化模拟数据后，验证商品和订单数据写入 openGauss。
- 触发 Spark 分析后，验证分析结果表被更新。
- 在看板页面验证图表刷新。
