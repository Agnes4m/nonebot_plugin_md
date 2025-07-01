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


@cmd.handle()
async def _(
    matcher: Matcher,
    event: Event,
    args: Message = CommandArg(),
):
    args_msg = args.extract_plain_text()
    msg = await mdbot(event.get_user_id(), args_msg)
    if isinstance(msg, str):
        await matcher.finish(msg)
    else:
        await UniMessage.image(raw=msg).send()


@b30.handle()
async def _(
    matcher: Matcher,
    event: Event,
    args: Message = CommandArg(),
):
    args_msg = args.extract_plain_text()
    args_msg = "b30" + args_msg
    msg = await mdbot(event.get_user_id(), args_msg)
    if isinstance(msg, str):
        await matcher.finish(msg)
    else:
        await UniMessage.image(raw=msg).send()
