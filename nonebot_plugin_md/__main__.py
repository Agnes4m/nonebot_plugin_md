from nonebot import on_shell_command
from nonebot.matcher import Matcher
from .message import help_message
from nonebot.rule import ArgumentParser
from nonebot.rule import ArgumentParser, Namespace
from typing import List, Optional
from nonebot import logger, on_command, on_shell_command
from nonebot.matcher import Matcher
from nonebot.params import Arg, ArgPlainText, CommandArg, ShellCommandArgs

from nonebot.typing import T_State
from nonebot_plugin_saa import Image, MessageFactory, MessageSegmentFactory, Text

cmd_generate_parser = ArgumentParser("md")
cmd_generate = on_shell_command(
    "md",
    parser=cmd_generate_parser,
    aliases={"喵斯快跑"},
    priority=2,
)


@cmd_generate.handle()
async def _(matcher: Matcher, args: Namespace = ShellCommandArgs()):
    texts: List[str] = args.text
    if texts[0] == "update":
        ...
