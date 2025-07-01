import json
from pathlib import Path
from typing import Tuple

import aiofiles
import aiohttp
from lxml import etree
from nonebot.log import logger

from .message import player_url, search_url

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0",  # noqa: E501
}

data_path = Path("data/md_data")


class MusicDataRepository:
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self._musics = None
        self._dif = None
        self._musics_names = None

    async def get_musics(self) -> dict:
        if self._musics is None:
            self._musics = await self._load_json_file("musics.json")
        return self._musics

    async def get_dif_data(self) -> dict:
        if self._dif is None:
            self._dif = await self._load_json_file("dif.json")
        return self._dif

    async def get_music_names(self) -> list:
        if self._musics_names is None:
            self._musics_names = await self._load_json_file("musics_name.json")
        return self._musics_names or []

    async def save_musics(self, data: dict) -> bool:
        return await self._save_json_file("musics.json", data)

    async def save_dif_data(self, data: dict) -> bool:
        return await self._save_json_file("dif.json", data)

    async def save_music_names(self, data: list) -> bool:
        return await self._save_json_file("musics_name.json", data)

    async def _load_json_file(self, filename: str) -> dict:
        try:
            async with aiofiles.open(
                self.data_path.joinpath(filename),
                mode="r",
                encoding="utf-8",
            ) as f:
                return json.loads(await f.read())
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse {filename}: {e}")
            return {}

    async def _save_json_file(self, filename: str, data: dict) -> bool:
        try:
            async with aiofiles.open(
                self.data_path.joinpath(filename),
                mode="w",
                encoding="utf-8",
            ) as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=4))

        except Exception as e:
            logger.error(f"Failed to save {filename}: {e}")
            return False
        return True


repo = MusicDataRepository(data_path)


async def url_to_byte(url: str):
    """获取URL数据的字节流"""

    async with (
        aiohttp.ClientSession() as session,
        session.get(url, headers=headers, timeout=600) as response,
    ):
        if response.status == 200:
            return await response.read()
        return None


async def url_to_msg(url: str):
    """获取URL数据的字节流"""

    async with (
        aiohttp.ClientSession() as session,
        session.get(url, headers=headers, timeout=600) as response,
    ):
        if response.status == 200:
            return await response.text()
        return None


async def level_dif(level: str):
    dif = await load_json_file(data_path.joinpath("dif.json"))
    if level in dif:
        return dif[level]
    return "您玩的真的是暮色大师吗"


async def load_json_file(file_path: Path) -> dict:
    """统一的异步JSON文件读取"""
    try:
        async with aiofiles.open(file_path, mode="r", encoding="utf-8") as f:
            return json.loads(await f.read())
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


async def save_json_file(file_path: Path, data: dict) -> bool:
    """统一的异步JSON文件保存"""
    try:
        async with aiofiles.open(file_path, mode="w", encoding="utf-8") as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=4))

    except Exception as e:
        logger.error(f"Failed to save {file_path}: {e}")
        return False
    return True


async def bindname(qq: str, name: str) -> Tuple[bool, str]:
    md_name, md_uid, only_one = await name2uid(name)
    if not md_uid:
        return False, "找不到该玩家名称"

    if not only_one:
        return False, "找到多个玩家，请使用UID绑定"

    success = await save_player(qq, md_name, md_uid, repo)
    return success, md_name if success else "绑定失败"


async def binduid(qq: str, uid: str) -> Tuple[bool, str]:
    name = await uid2name(uid)
    logger.info(f"开始绑定{name}({uid})")
    if name == "User not Found":
        return False, "无效的玩家UID"

    success = await save_player(qq, name, uid)
    return success, name if success else "绑定失败"


async def uid2name(uid: str) -> str:
    response = await url_to_msg(url=player_url + uid)
    if not response:
        logger.error("获取玩家信息失败")
        return "User not Found"
    tree = etree.HTML(response)

    name_element = tree.xpath(
        '//*[@id="app"]/section/div/div/div/section/div/div/div[1]/div/div[1]/h1',
    )[0].text

    return (
        name_element[17 : len(name_element) - 15] if name_element else "User not Found"
    )


async def name2uid(name: str) -> Tuple[str, str, bool]:
    response = await url_to_msg(url=search_url + name)
    players = json.loads(response)
    return (
        (players[0][0], players[0][1], len(players) == 1) if players else ("", "", False)
    )


async def save_player(player_qq: str, player_name: str, player_uid: str) -> bool:
    player_data = await repo.get_musics()
    player_data[player_qq] = [player_name, player_uid]
    return await repo.save_musics(player_data)


async def unbind(qq: str, repo: MusicDataRepository) -> Tuple[bool, str]:
    """
    解除账号绑定
    返回: (是否成功, 玩家名称或错误信息)
    """
    player_data = await repo.get_musics()

    if qq not in player_data:
        return False, "该账号未绑定"

    name = player_data[qq][0]
    del player_data[qq]

    success = await repo.save_musics(player_data)
    return success, name if success else "解绑失败"
