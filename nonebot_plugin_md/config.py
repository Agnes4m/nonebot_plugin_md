from nonebot import get_driver
from pydantic import BaseModel


class ConfigModel(BaseModel):
    is_b30: bool = True


config: ConfigModel = ConfigModel.parse_obj(get_driver().config.dict())
