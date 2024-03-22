from lxml import etree
import json

# import io
from fuzzywuzzy import fuzz, process
from .message import (
    player_url,
    dif_url,
    albums_url,
    search_url,
    json_path,
    help_message,
    base_url,
)
from pathlib import Path
from .utils import url_to_msg

# from .image import b30_image

data_path = Path("data/md_data")

# //*[@id="app"]/section/div/div/div/nav[2]/div[1]/figure/img
# //*[@id="app"]/section/div/div/div/nav[3]/div[1]/figure/img
# /html/body/div/section/div/div/div/nav[2]/div[1]/figure/img


async def b30(md_uid):
    # response = await url_to_msg(url='https://musedash.moe/player/86be39866f9911ebbc1d0242ac110039')
    response = await url_to_msg(url=player_url + md_uid)
    tree = etree.HTML(response)
    spans = tree.xpath("/html/body/div/section/div/div/div//nav")  # 解析
    ptt = tree.xpath(
        '//*[@id="app"]/section/div/div/div/section/div/div/div[2]/div/div[1]/h1'
    )[0].text
    ptt = ptt.replace(" ", "")
    ptt = ptt.replace("\n", "")
    songs = {}
    num = 1
    for i in range(len(spans)):
        if i == 0:
            continue

        song = spans[i].xpath("./div[4]/div/a[2]/@href")

        song_chars = song[0].split("/")
        song_uid = song_chars[2]
        song_dif = int(song_chars[3])
        acc = spans[i].xpath("./div[3]/div/p[1]")
        song_acc = float(acc[0].text[:-1]) / 100

        break_flag = False
        for song in songs:
            if songs[song]["uid"] == song_uid and songs[song]["dif"] == song_dif:
                break_flag = True
                if song_acc > songs[song]["acc"]:
                    songs[song]["acc"] = song_acc
                break

        if break_flag:
            continue

        info = {}
        info["uid"] = song_uid
        info["dif"] = song_dif
        info["acc"] = song_acc
        info["ptt"] = 0
        pic = tree.xpath(
            f"/html/body/div/section/div/div/div/nav[{i+1}]/div[1]/figure/img"
        )[0].get("src")
        pic_url = base_url + pic
        info["pic"] = pic_url
        songs[num] = info
        num += 1

    with open(data_path.joinpath("musics.json"), "rb") as f:
        music_data = json.load(f)

    for song in songs:
        songs[song]["diffdiff"] = music_data[songs[song]["uid"]]["diffdiff"][
            songs[song]["dif"]
        ]
        songs[song]["ptt"] = (
            music_data[songs[song]["uid"]]["diffdiff"][songs[song]["dif"]]
            * songs[song]["acc"]
        )
        songs[song]["dif"] = music_data[songs[song]["uid"]]["difficulty"][
            songs[song]["dif"]
        ]
        songs[song]["name"] = music_data[songs[song]["uid"]]["ChineseS"]["name"]

        songs[song]["acc"] = "{:.2%}".format(songs[song]["acc"])
        songs[song]["diffdiff"] = "{:.2f}".format(songs[song]["diffdiff"])
    # print(songs)
    songs = sorted(songs.items(), key=lambda x: x[1]["ptt"], reverse=True)
    # 文字输出
    message = f"姓名:{await uid2name(md_uid)}"
    message += "\n综合评分:{0}".format(ptt)
    for i in range(30):
        if i >= len(songs):
            break
        message += "\n{0}、{1}({2}) {3}".format(
            i + 1, songs[i][1]["name"], songs[i][1]["diffdiff"], songs[i][1]["acc"]
        )
    message += "\npower by Agnes4m & moe & Nonebot2"

    # 图片输出
    # master_data = {"uid": md_uid, "name": await uid2name(md_uid), "ptt": ptt}
    # message_image = await b30_image(songs, master_data)
    # message = io.BytesIO()
    # message_image.save(message, format="PNG")
    return message


async def name2uid(name):
    response = await url_to_msg(url=search_url + name)
    players = json.loads(response)

    if len(players) == 0:
        return "", "", False
    else:
        md_name = players[0][0]
        md_uid = players[0][1]
        if len(players) == 1:
            return md_name, md_uid, True
        else:
            return md_name, md_uid, False


async def uid2name(uid):
    response = await url_to_msg(url=player_url + uid)
    tree = etree.HTML(response)
    name = tree.xpath(
        '//*[@id="app"]/section/div/div/div/section/div/div/div[1]/div/div[1]/h1'
    )[0].text
    return name[17 : len(name) - 15]


async def qq2uid(qq):
    player_data = {}
    try:
        with open(json_path, "rb") as f:
            player_data = json.load(f)

    except Exception:
        with open(json_path, "w") as f:
            json.dump(player_data, f)

    if qq in player_data:
        return True, player_data[qq][1]
    else:
        return False, ""


async def save_player(player_qq, player_name, player_uid):
    player_info = []
    player_info.append(player_name)
    player_info.append(player_uid)

    player_data = {}
    try:
        with open(json_path, "rb") as f:
            player_data = json.load(f)

    except Exception:
        with open(json_path, "w") as f:
            json.dump(player_data, f)

    player_data[player_qq] = player_info
    with open(json_path, "w") as f:
        json.dump(player_data, f)


async def bindname(qq, name):
    md_name, md_uid, only_one = await name2uid(name)
    if only_one:
        await save_player(qq, md_name, md_uid)
        return True, md_name
    else:
        return False, ""


async def binduid(qq, uid):
    name = uid2name(uid)
    if name == "User not Found":
        return False, name
    save_player(qq, name, uid)
    return True, name


async def unbind(qq):
    player_data = {}
    try:
        with open(json_path, "rb") as f:
            player_data = json.load(f)

    except Exception:
        with open(json_path, "w") as f:
            json.dump(player_data, f)

    if qq in player_data:
        name = player_data[qq][0]
        del player_data[qq]
        with open(json_path, "w") as f:
            json.dump(player_data, f)

        return True, name
    else:
        return False, ""


async def update_musics():
    data_path.mkdir(parents=True, exist_ok=True)

    response = await url_to_msg(url=dif_url)
    dif = json.loads(response)

    response = await url_to_msg(url=albums_url)
    albums = json.loads(response)

    musics = {}
    for album in albums:
        for music in albums[album]["music"]:
            musics[music] = albums[album]["music"][music]
            musics[music]["diffdiff"] = [0, 0, 0, 0, 0]

    for array in dif:
        musics[array[0]]["diffdiff"][array[1]] = array[4]

    level_dif = {}
    for i in range(12):
        level_dif[str(i + 1)] = {}
    level_dif["?"] = {}
    level_dif["¿"] = {}

    chart_id = 1
    for uid in musics:
        for i in range(4):
            if musics[uid]["difficulty"][i] != "0":
                song = {}
                song["name"] = musics[uid]["name"]
                song["dif"] = musics[uid]["diffdiff"][i]
                try:
                    level_dif[musics[uid]["difficulty"][i]][chart_id] = song
                except Exception:
                    ...
                chart_id += 1

    for level in level_dif:
        level_dif[level] = sorted(
            level_dif[level].items(), key=lambda x: x[1]["dif"], reverse=True
        )
        record = "Lv.{0}".format(level)
        for song in level_dif[level]:
            record += "\n{0}({1:.2f})".format(song[1]["name"], song[1]["dif"])
        level_dif[level] = record

    musics_names = []
    for uid in musics:
        musics_names.append(musics[uid]["name"])

    with open(data_path.joinpath("musics.json"), "w") as f:
        json.dump(musics, f)

    with open(data_path.joinpath("dif.json"), "w") as f:
        json.dump(level_dif, f)

    with open(data_path.joinpath("musics_name.json"), "w") as f:
        json.dump(musics_names, f)


async def level_dif(level: str):
    with open(data_path.joinpath("dif.json"), "rb") as f:
        dif = json.load(f)

    if level in dif:
        return dif[level]
    else:
        return "您玩的真的是暮色大师吗"


async def song_info(name):
    with open(data_path.joinpath("musics_name.json"), "rb") as f:
        musics_name = json.load(f)

    with open(data_path.joinpath("musics.json"), "rb") as f:
        musics_data = json.load(f)

    close_name = process.extractOne(name, musics_name, scorer=fuzz.token_sort_ratio)
    if len(close_name) == 0:
        return "找不到捏，再好好想想"

    message = close_name[0]
    for uid in musics_data:
        if musics_data[uid]["name"] == close_name[0]:
            message += "\n作者:{0}".format(musics_data[uid]["author"])
            message += "\nbpm:{0}".format(musics_data[uid]["bpm"])
            message += "\n难度:"
            if musics_data[uid]["difficulty"][0] != "0":
                message += "\n萌新:{0}({1:.2f})".format(
                    musics_data[uid]["difficulty"][0], musics_data[uid]["diffdiff"][0]
                )
            if musics_data[uid]["difficulty"][1] != "0":
                message += "\n高手:{0}({1:.2f})".format(
                    musics_data[uid]["difficulty"][1], musics_data[uid]["diffdiff"][1]
                )
            if musics_data[uid]["difficulty"][2] != "0":
                message += "\n大触:{0}({1:.2f})".format(
                    musics_data[uid]["difficulty"][2], musics_data[uid]["diffdiff"][2]
                )
            if musics_data[uid]["difficulty"][3] != "0":
                message += "\n里谱:{0}({1:.2f})".format(
                    musics_data[uid]["difficulty"][3], musics_data[uid]["diffdiff"][3]
                )
            message += "\n谱师:"
            for p in musics_data[uid]["levelDesigner"]:
                if p is not None:
                    message += "\n{0}".format(p)

    return message


async def mdbot(qq: str, message: str):
    # try:
    message_chars = message.split(" ")
    if len(message_chars) == 0:
        return help_message
    if message_chars[0] in ["帮助", "help"]:
        return help_message
    if message_chars[0] in ["更新", "update"]:
        await update_musics()
        return "更新完了"
    if message_chars[0] in ["绑定", "bindname", "binduid"]:
        success, name = await bindname(qq, message_chars[1])
        print(success)
        if success:
            return "就你小子叫{0}({1})啊！".format(name, qq)
        else:
            return "找不到捏，试试用uid绑定"
    if message_chars[0] in ["绑定uid", "binduid"]:
        success, name = await binduid(qq, message_chars[1])
        if success:
            return "就你小子叫{0}({1})啊！".format(name, qq)
        else:
            return "你这uid有问题啊"
    if message_chars[0] in ["解绑", "unbind"]:
        success, name = await unbind(qq)
        if success:
            return "呜呜呜{0}({1})再见了".format(name, qq)
        else:
            return "找不到捏，可能是没绑，试试/md help"
    if message_chars[0] == "b30":
        success, uid = await qq2uid(qq)
        if success:
            return await b30(uid)
        else:
            return "找不到捏，可能是没绑，试试/md help"
    if message_chars[0] == "b30name":
        md_name, md_uid, success = await name2uid(message_chars[1])
        if md_uid != "":
            return await b30(md_uid)
    if message_chars[0] == "dif":
        return await level_dif(message_chars[1])
    if message_chars[0] == "song":
        return await song_info(message_chars[1])
    if message_chars[0] == "test":
        return "欸嘿！"
    else:
        return "您可真会玩!试试/md help"


# except Exception as E:
#     return f"{E}出错了！试试/md help"
