# _*_ coding: utf-8 _*_
"""
Author: 'LingLing'
Date: 2022/07/19
"""
import asyncssh
import asyncio
import typing as t


class CmdResultHandle:

    def __init__(
        self,
        stdout: t.Union[bytes, str],
        stderr: t.Union[bytes, str] = None,
        code: int = 0,
        sink: t.Callable = None,
        is_print: bool = True
    ):
        self.is_print = is_print
        self.stdout = stdout.strip() if isinstance(stdout, str) else stdout.decode()
        self.stderr = stderr.strip() if isinstance(stderr, str) else stderr.decode()
        self.code = code
        self.sink = sink

    async def std_handle(self) -> None:
        if self.is_print:
            print(self.__str__())
        if self.sink:
            if asyncio.iscoroutinefunction(self.sink):
                await self.sink()
            else:
                self.sink()

    def __str__(self) -> any:
        return self.stdout.strip() + self.stderr.strip()

    def __bool__(self) -> bool:
        return self.code == 0


async def cmd_result(cmd: str, is_print: bool = False, sink: t.Union[t.Callable, t.Awaitable] = None) -> CmdResultHandle:
    """
    本地执行 shell 返回结果
    """
    proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    req = CmdResultHandle(stdout, stderr, code=proc.returncode, sink=sink, is_print=is_print)
    await req.std_handle()
    return req


async def cmd_real(cmd: str) -> t.Optional[bool]:
    """
    本地执行 shell 分片结果
    """
    pass


async def cmd_remote(cmd: str, host: str) -> t.Optional[str]:
    """
    远程执行 shell 返回结果
    """
    async with asyncssh.connect(host, port=22, client_keys=[], passphrase='', known_hosts=None) as conn:
        result = await conn.run(cmd, check=True)

        return result.stdout
