# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2023/03/24
"""
from aerich import DowngradeError

from OperationFrame.config import config
from OperationFrame.utils.aerich import aer
from OperationFrame.utils.cbvmenu import CommonCbv
from OperationFrame.utils.cbvmenu.constant import TAG_DB
from OperationFrame.utils.log import logger


class DbMysqlInit(CommonCbv):

    async def run(self):
        try:
            await aer.init_db(True)
            logger.info(f"{config.MYSQL_REGISTER_MODEL} 初始化数据库模型成功")
        except FileExistsError:
            logger.warning(f"{config.MYSQL_REGISTER_MODEL} 数据库表已初始化，删除 {aer.location} 可重新初始化")

    class Meta:
        name = '数据库 mysql 初始化'
        sign = 'db_mysql_init'
        tag = TAG_DB


class DbMysqlMigrate(CommonCbv):

    async def run(self, name="update"):
        try:
            ret: str = await aer.migrate(name)
        except AttributeError:
            logger.warning(f"迁移任务:{name} | {config.MYSQL_REGISTER_MODEL} 模型表不存在, 请先初始化表")
            return

        if not ret:
            logger.warning(f"迁移任务:{name} | {config.MYSQL_REGISTER_MODEL} 模型未检测到任何更改")
            return
        logger.info(f"迁移任务:{name} | {config.MYSQL_REGISTER_MODEL} 模型迁移成功")

        ret: list = await aer.upgrade()
        if not ret:
            logger.warning(f"更新任务:{name} | {config.MYSQL_REGISTER_MODEL} 找不到更新项目")
        else:
            for version_file in ret:
                logger.info(f"更新任务:{name} | 成功更新 {version_file}")

    class Meta:
        name = '数据库 mysql 更新表'
        sign = 'db_mysql_migrate'
        tag = TAG_DB


class DbMysqlDownGrade(CommonCbv):

    async def run(self, version: str = -1):
        try:
            files: list = await aer.downgrade(version, False)
        except DowngradeError as e:
            logger.warning(f"{config.MYSQL_REGISTER_MODEL} 回滚操作未执行, 错误: {str(e)}")
            return
        for file in files:
            logger.info(f"{config.MYSQL_REGISTER_MODEL} {file} 成功回滚到版本 {version}")

    class Meta:
        name = '数据库 mysql 回滚表'
        sign = 'db_mysql_downgrade'
        tag = TAG_DB


class DbMysqlHistory(CommonCbv):

    async def run(self):
        try:
            versions: list = await aer.history()
        except FileNotFoundError:
            logger.warning(f"{config.MYSQL_REGISTER_MODEL} 未查询到指定迁移文件, 请尝试初始化数据表")
            return

        if not versions:
            logger.warning(f"{config.MYSQL_REGISTER_MODEL} 不存在迁移历史")
            return
        logger.info(f"{config.MYSQL_REGISTER_MODEL} 迁移历史文件如下:")
        for version in versions:
            logger.info(version)

    class Meta:
        name = '数据库 mysql 更新历史'
        sign = 'db_mysql_history'
        tag = TAG_DB


class DbMysqlHead(CommonCbv):

    async def run(self):
        try:
            heads: list = await aer.heads()
        except FileNotFoundError:
            logger.warning(f"{config.MYSQL_REGISTER_MODEL} 未查询到指定迁移文件, 请尝试初始化数据表")
            return

        if not heads:
            logger.warning(f"{config.MYSQL_REGISTER_MODEL} 不存在迁移历史")
            return
        logger.info(f"{config.MYSQL_REGISTER_MODEL} 当前迁移历史文件如下:")
        for version in heads:
            logger.info(version)

    class Meta:
        name = '数据库 mysql 当前版本迁移文件'
        sign = 'db_mysql_heads'
        tag = TAG_DB
