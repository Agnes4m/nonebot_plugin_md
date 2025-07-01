from nonebot import get_driver
from pydantic import BaseModel


class ConfigModel(BaseModel):
    is_b30: bool = True


config: ConfigModel = ConfigModel.model_validate(get_driver().config.model_dump())
