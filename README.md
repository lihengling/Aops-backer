## Aops-backer

> OperationFrame：一个异步 api 框架

> 本项目将以 OperationFrame 为后端开发一套运维管理后台接口

### 功能
- 基于 jwt 的接口权限校验： rbac 
- restful 接口快速生成： curd 
- 异步任务后台执行： arq 
- http/rpc 两种访问方式
- 菜单项目任务执行

### 相关包

- pydantic = 1.9.1
- toml = 0.10.2
- redis = 4.5.4
- orjson = 3.8.10
- loguru = 0.6.0
- tortoise-orm[asyncmy] = 0.19.2
- aerich = 0.6.3
- uvicorn[standard] = 0.18.2
- aiomysql = 0.1.1
- fastapi = 0.79.0
- bcrypt = 4.0.1
- async-property = 0.2.1
- PyJWT = 2.6.0
- werkzeug = 2.2.0
- arq = 0.25.0
- fastapi_crudrouter = 0.8.6
- PyJWT = 2.6.0
- gunicorn = 20.1.0
- python-multipart = 0.0.6

### 关于 框架 使用

> 启动服务时请修改 env.toml 环境配置

> 协程服务中不建议使用同步组件

> mysql 版本 >= 5.7，推荐 mysql8.0

> redis 版本 >= 3.2，推荐 redis3.2.12

### 启动服务

> python3 main.py Action [options]

