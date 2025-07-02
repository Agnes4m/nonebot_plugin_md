import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple, cast

from fuzzywuzzy import fuzz, process
from lxml import etree
from nonebot.log import logger
from nonebot_plugin_htmlrender import template_to_pic as t2p

from .message import (
    albums_url,
    base_url,
    dif_url,
    help_message,
    player_url,
)
from .model import SongInfo
from .utils import (
    bindname,
    binduid,
    find_existing_song,
    name2uid,
    repo,
    uid2name,
    unbind,
    update_song_info,
    url_to_msg,
)

data_path = Path("data/md_data")


async def parse_song_href(href: str) -> Tuple[str, int]:
    parts = href.split("/")
    return parts[2], int(parts[3])


def clean_text(text: str) -> str:
    return text.replace(" ", "").replace("\n", "")


async def b30(md_uid: str) -> bytes:
    response = await url_to_msg(url=player_url + md_uid)
    tree = etree.HTML(response)

    ptt_element = tree.xpath(
        '//*[@id="app"]/section/div/div/div/section/div/div/div[2]/div/div[1]/h1',
    )
    if not ptt_element:
        return "无法解析玩家数据"

    ptt = clean_text(ptt_element[0].text)
    songs = await parse_songs(tree, await repo.get_musics())
    logger.debug(songs)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return await t2p(
        template_path=Path(__file__).parent / "template",
        template_name="b30.html",
        templates={
            "songs": songs,
            "player_name": await uid2name(md_uid),
            "overall_ptt": ptt[1:-2],
            "current_time": current_time,
        },
    )


async def parse_songs(tree: etree._Element, music_data: dict) -> Dict[int, SongInfo]:
    songs = {}
    song_elements = tree.xpath("/html/body/div/section/div/div/div//nav")

    for i, element in enumerate(song_elements[1:], 1):
        try:
            # 提取歌曲链接
            song_link = element.xpath("./div[4]/div/a[2]/@href")
            if not song_link:
                continue
            song_uid, song_dif = await parse_song_href(song_link[0])

            # 提取准确率, 总分和人物
            acc_element = element.xpath("./div[3]/div/p[1]/text()")
            if not acc_element:
                logger.debug(f"元素 {i} 中没有找到准确率数据")
                continue
            acc = float(acc_element[0].strip("%")) / 100
            song_socre = str(element.xpath("./div[3]/div/p[2]/text()")[0])
            song_pat, song_role = (
                str(element.xpath("./div[3]/div/p[3]/text()")[0])
            ).split("/")

            # 验证音乐数据
            if song_uid not in music_data:
                continue

            music = music_data[song_uid]
            diff = music["diffdiff"][song_dif]

            song_info = {
                "uid": song_uid,
                "dif": music["difficulty"][song_dif],
                "acc": acc,
                "ptt": diff * acc,
                "diffdiff": diff,
                "name": music["ChineseS"]["name"],
                "pic": (
                    base_url + element.xpath(".//img/@src")[0]
                    if element.xpath(".//img/@src")
                    else ""
                ),
                "score": song_socre,
                "role": song_role,
                "pat": song_pat,
            }
            song_info = cast(SongInfo, song_info)

            existing_song = find_existing_song(songs, song_info)
            if existing_song:
                if acc > existing_song["acc"]:
                    update_song_info(existing_song, song_info)
                continue

            songs[len(songs) + 1] = song_info

        except Exception as e:
            logger.warning(f"解析歌曲 {i} 失败: {e}")
            continue

    # 按PTT降序排序并取前30
    return dict(sorted(songs.items(), key=lambda x: x[1]["ptt"], reverse=True)[:30])


async def update_musics() -> bool:
    try:
        data_path.mkdir(parents=True, exist_ok=True)

        dif_response, albums_response = await asyncio.gather(
            url_to_msg(dif_url),
            url_to_msg(albums_url),
        )

        musics = {}
        for album in json.loads(albums_response).values():
            for uid, music in album.get("music", {}).items():
                musics[uid] = music
                musics[uid]["diffdiff"] = [0.0] * 5

        for entry in json.loads(dif_response):
            musics[entry[0]]["diffdiff"][entry[1]] = entry[4]

        level_dif = {str(i): {} for i in range(1, 13)}
        level_dif.update({"?": {}, "¿": {}})

        chart_id = 1
        for _, music in musics.items():
            for i, diff in enumerate(music["difficulty"]):
                if diff != "0":
                    level_dif[diff][chart_id] = {
                        "name": music["name"],
                        "dif": music["diffdiff"][i],
                    }
                    chart_id += 1

        save_tasks = [
            repo.save_musics(musics),
            repo.save_dif_data(
                {
                    level: "Lv.{}\n{}".format(
                        level,
                        "\n".join(
                            f"{s['name']}({s['dif']:.2f})"
                            for s in sorted(
                                songs.values(),
                                key=lambda x: x["dif"],
                                reverse=True,
                            )
                        ),
                    )
                    for level, songs in level_dif.items()
                },
            ),
            repo.save_music_names([m["name"] for m in musics.values()]),
        ]

        await asyncio.gather(*save_tasks)

    except Exception as e:
        logger.error(f"Music data update failed: {e}")
        return False
    return True


async def mdbot(qq: str, message: str) -> str:
    message_chars = message.strip().split()
    if not message_chars:
        return help_message

    cmd = message_chars[0].lower()

    command_handlers = {
        "帮助": lambda: help_message,
        "help": lambda: help_message,
        "更新": lambda: update_musics_wrapper(repo),
        "update": lambda: update_musics_wrapper(repo),
        "绑定": lambda: bind_wrapper(qq, message_chars),
        "bindname": lambda: bind_wrapper(qq, message_chars),
        "绑定uid": lambda: bind_uid_wrapper(qq, message_chars),
        "binduid": lambda: bind_uid_wrapper(qq, message_chars),
        "解绑": lambda: unbind_wrapper(qq),
        "unbind": lambda: unbind_wrapper(qq),
        "b30": lambda: b30_wrapper(qq),
        "b30name": lambda: b30_name_wrapper(message_chars),
        "dif": lambda: dif_wrapper(message_chars),
        "song": lambda: song_info_wrapper(message_chars),
        "test": lambda: "欸嘿！",
    }

    handler = command_handlers.get(cmd, lambda: "您可真会玩!试试/md help")
    return await handler()


async def update_musics_wrapper() -> str:
    success = await update_musics(repo)
    return "更新完了" if success else "更新失败"


async def bind_wrapper(qq: str, message_chars: list) -> str:
    if len(message_chars) < 2:
        return "请输入要绑定的名称"
    success, name = await bindname(qq, message_chars[1])
    return f"就你小子叫{name}({qq})啊！" if success else "找不到捏，试试用uid绑定"


async def bind_uid_wrapper(qq: str, message_chars: list) -> str:
    if len(message_chars) < 2:
        return "请输入要绑定的UID"
    success, name = await binduid(qq, message_chars[1])
    return f"就你小子叫{name}({qq})啊！" if success else "你这uid有问题啊"


async def unbind_wrapper(qq: str) -> str:
    success, name = await unbind(qq)
    return (
        f"呜呜呜{name}({qq})再见了" if success else "找不到捏，可能是没绑，试试/md help"
    )


async def b30_wrapper(qq: str) -> str:
    # try:
    player_data = await repo.get_musics()
    if qq not in player_data:
        return "找不到捏，可能是没绑，试试/md help"
    return await b30(player_data[qq][1])
    # except Exception as e:
    #     logger.error(f"B30 query failed: {e}")
    #     return "获取数据失败，请稍后再试"


async def b30_name_wrapper(message_chars: list) -> str:
    if len(message_chars) < 2:
        return "请输入玩家名称"
    md_name, md_uid, _ = await name2uid(message_chars[1])
    return await b30(md_uid) if md_uid else "找不到该玩家"


async def dif_wrapper(message_chars: list) -> str:
    if len(message_chars) < 2:
        return "请输入难度等级"
    dif_data = await repo.get_dif_data()
    return dif_data.get(message_chars[1], "您玩的真的是暮色大师吗")


async def song_info_wrapper(message_chars: list) -> str:
    if len(message_chars) < 2:
        return "请输入歌曲名称"
    return await song_info(message_chars[1])


async def song_info(name: str) -> str:
    try:
        musics_names = await repo.get_music_names()
        musics_data = await repo.get_musics()

        close_name = process.extractOne(
            name,
            musics_names,
            scorer=fuzz.token_sort_ratio,
        )
        if not close_name:
            return "找不到捏，再好好想想"

        for _, music in musics_data.items():
            if music["name"] == close_name[0]:
                return build_song_info_message(music)

    except Exception as e:
        logger.error(f"Song info query failed: {e}")
        return "获取歌曲信息失败"
    return "歌曲数据不完整"


def build_song_info_message(music: dict) -> str:
    message = [music["name"]]
    message.append(f"作者:{music.get('author', '未知')}")
    message.append(f"bpm:{music.get('bpm', '未知')}")

    difficulties = []
    for i, diff in enumerate(music["difficulty"]):
        if diff != "0":
            difficulties.append(
                f"{['萌新','高手','大触','里谱'][i]}:{diff}({music['diffdiff'][i]:.2f)}",
            )

    if difficulties:
        message.append("难度:\n" + "\n".join(difficulties))

    designers = [d for d in music.get("levelDesigner", []) if d]
    if designers:
        message.append("谱师:\n" + "\n".join(designers))

    return "\n".join(message)
