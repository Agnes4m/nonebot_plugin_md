from typing import Optional, Set

from nonebot import get_driver
from pydantic import BaseModel


class ConfigModel(BaseModel):
    command_start: Set[str]

    pjsk_req_retry: int = 2
    pjsk_req_proxy: Optional[str] = None


config: ConfigModel = ConfigModel.parse_obj(get_driver().config.dict())
