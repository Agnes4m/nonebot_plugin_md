from typing import Optional

from pydantic import BaseModel, Field


class SongInfo(BaseModel):
    """歌曲信息数据模型"""

    uid: str = Field(..., description="歌曲唯一ID")
    dif: str = Field(..., description="难度名称")
    acc: float = Field(..., description="准确率(0-1)")
    ptt: float = Field(..., description="潜力值")
    diffdiff: float = Field(..., description="谱面定数")
    name: str = Field(..., description="歌曲名称")
    pic: Optional[str] = Field(None, description="歌曲封面URL")
    score: str = Field(..., description="分数")
    role: str = Field(..., description="歌曲使用搭档")
    pat: str = Field(..., description="歌曲使用宠物")

    @property
    def formatted_acc(self) -> str:
        return f"{self.acc:.2%}"

    @property
    def formatted_diffdiff(self) -> str:
        return f"{self.diffdiff:.2f}"
