from nonebot import require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_saa")

from . import __main__ as __main__  # noqa: E402
from .config import ConfigModel  # noqa: E402

__version__ = "0.1.0"
__plugin_meta__ = PluginMetadata(
    name="Sekai Stickers",
    description="基于 NoneBot2 的 MUSE DASH查询插件",
    usage="使用指令 `pjsk -h` 查看帮助",
    type="application",
    homepage="https://github.com/Agnes4m/nonebot_plugin_pjsk",
    config=ConfigModel,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_saa"),
    extra={
        "version": __version__,
        "author": ["Agnes4m <Z735803792@163.com>"],
    },
)
