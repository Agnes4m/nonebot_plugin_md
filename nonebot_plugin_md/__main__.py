from nonebot import on_command
from nonebot.adapters import Event, Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot_plugin_alconna import UniMessage

from .b30 import mdbot
from .config import config

if config.is_b30:
    b30 = on_command("b30", priority=1)
cmd = on_command("md", priority=2)


async def handle_command(
    matcher: Matcher,
    event: Event,
    args: Message,
    prefix: str = "",
):
    args_msg = prefix + args.extract_plain_text()
    msg = await mdbot(event.get_user_id(), args_msg)

    if isinstance(msg, str):
        await matcher.finish(msg)
    else:
        await UniMessage.image(raw=msg).send()


@cmd.handle()
async def handle_md(matcher: Matcher, event: Event, args: Message = CommandArg()):
    """处理md命令"""
    await handle_command(matcher, event, args)


if config.is_b30:

    @b30.handle()
    async def handle_b30(matcher: Matcher, event: Event, args: Message = CommandArg()):
        """处理b30命令"""
        await handle_command(matcher, event, args, "b30")
