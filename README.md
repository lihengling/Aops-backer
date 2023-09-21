## OperationFrame

> 这是一个基于 Python 3.10+ 的 异步运维框架, 提供菜单终端与业务接口的执行任务方式
>
> 分离终端执行与api执行方式，集中两者的业务接口
>
> ApiFrame 是一个 fastapi 的快速开发脚手架，提供普通接口与异步任务、定时任务功能、rpc接口功能

### 相关包

- asyncssh = 2.11.0
- tortoise-orm[asyncmy] = 0.19.2
- fastapi = 0.79.0
- uvicorn = 0.18.2
- loguru = 0.6.0
- aerich = 0.6.3
- async-property = 0.2.1
- orjson = 3.6.7
- PyJWT = 2.6.0
- werkzeug = 2.2.3
- bcrypt = 4.0.1
- toml = 0.10.2
- arq = 0.25.0
- fastapi_crudrouter = 0.8.6
- redis = 4.5.4

### 关于 框架 使用

> 启动服务时请修改 env.toml 环境配置

> 协程服务中不建议使用同步组件

> mysql 版本 >= 5.7，推荐 mysql8.0

> redis 版本 >= 3.2，推荐 redis3.2.12

### 启动服务

> python3 main.py Action [options]

