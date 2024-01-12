from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, RawCommand, CommandStart
from nonebot.adapters import Event, Message
from nonebot_plugin_saa import Image, MessageFactory
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
    start=CommandStart(),
    raw=RawCommand(),
):
    args_msg = args.extract_plain_text()
    keyword = raw.replace(start, "").replace(args_msg, "")

    if keyword == "b30":
        args_msg = "md b30" + args_msg
    msg = await mdbot(event.get_user_id(), args_msg)
    if isinstance(msg, str):
        await matcher.finish(msg)
    else:
        await MessageFactory([Image(msg)]).send()


@b30.handle()
async def _(
    matcher: Matcher,
    event: Event,
    args: Message = CommandArg(),
):
    args_msg = args.extract_plain_text()
    args_msg = "md b30" + args_msg
    msg = await mdbot(event.get_user_id(), args_msg)
    if isinstance(msg, str):
        await matcher.finish(msg)
    else:
        await MessageFactory([Image(msg)]).send()
