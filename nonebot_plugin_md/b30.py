import os

import requests as requests
from lxml import etree
import json
from fuzzywuzzy import fuzz, process
from .message import player_url, dif_url, albums_url, search_url, json_path


def b30(md_uid):
    # response = requests.get(url='https://musedash.moe/player/86be39866f9911ebbc1d0242ac110039')
    response = requests.get(url=player_url + md_uid)
    tree = etree.HTML(response.text)
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
        songs[num] = info
        num += 1

    with open("./md_data/musics.json", "rb") as f:
        music_data = json.load(f)
    f.close()

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
    songs = sorted(songs.items(), key=lambda x: x[1]["ptt"], reverse=True)

    message = uid2name(md_uid)
    message += "\n"
    message += ptt
    for i in range(30):
        if i >= len(songs):
            break
        message += "\n{0}({1}) {2}".format(
            songs[i][1]["name"], songs[i][1]["diffdiff"], songs[i][1]["acc"]
        )
    return message


def name2uid(name):
    response = requests.get(url=search_url + name)
    players = json.loads(response.text)

    if len(players) == 0:
        return "", "", False
    else:
        md_name = players[0][0]
        md_uid = players[0][1]
        if len(players) == 1:
            return md_name, md_uid, True
        else:
            return md_name, md_uid, False


def uid2name(uid):
    response = requests.get(url=player_url + uid)
    tree = etree.HTML(response.text)
    name = tree.xpath(
        '//*[@id="app"]/section/div/div/div/section/div/div/div[1]/div/div[1]/h1'
    )[0].text
    return name[17 : len(name) - 15]


def qq2uid(qq):
    player_data = {}
    try:
        with open(json_path, "rb") as f:
            player_data = json.load(f)
        f.close()
    except:
        with open(json_path, "w") as f:
            json.dump(player_data, f)
        f.close()

    if qq in player_data:
        return True, player_data[qq][1]
    else:
        return False, ""


def save_player(player_qq, player_name, player_uid):
    player_info = []
    player_info.append(player_name)
    player_info.append(player_uid)

    player_data = {}
    try:
        with open(json_path, "rb") as f:
            player_data = json.load(f)
        f.close()
    except:
        with open(json_path, "w") as f:
            json.dump(player_data, f)
        f.close()

    player_data[player_qq] = player_info
    with open(json_path, "w") as f:
        json.dump(player_data, f)
    f.close()


def bindname(qq, name):
    md_name, md_uid, only_one = name2uid(name)
    if only_one:
        save_player(qq, md_name, md_uid)
        return True, md_name
    else:
        return False, ""


def binduid(qq, uid):
    name = uid2name(uid)
    if name == "User not Found":
        return False, name
    save_player(qq, name, uid)
    return True, name


def unbind(qq):
    player_data = {}
    try:
        with open(json_path, "rb") as f:
            player_data = json.load(f)
        f.close()
    except:
        with open(json_path, "w") as f:
            json.dump(player_data, f)
        f.close()

    if qq in player_data:
        name = player_data[qq][0]
        del player_data[qq]
        with open(json_path, "w") as f:
            json.dump(player_data, f)
        f.close()
        return True, name
    else:
        return False, ""


def update_musics():
    try:
        os.mkdir(r"./md_data")
    except:
        pass
    response = requests.get(url=dif_url)
    dif = json.loads(response.text)

    response = requests.get(url=albums_url)
    albums = json.loads(response.text)

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
                level_dif[musics[uid]["difficulty"][i]][chart_id] = song
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

    with open("./md_data/musics.json", "w") as f:
        json.dump(musics, f)
    f.close()

    with open("./md_data/dif.json", "w") as f:
        json.dump(level_dif, f)
    f.close()

    with open("./md_data/musics_name.json", "w") as f:
        json.dump(musics_names, f)
    f.close()


def level_dif(level):
    with open("./md_data/dif.json", "rb") as f:
        dif = json.load(f)
    f.close()
    if level in dif:
        return dif[level]
    else:
        return "您玩的真的是暮色大师吗"


def song_info(name):
    with open("./md_data/musics_name.json", "rb") as f:
        musics_name = json.load(f)
    f.close()

    with open("./md_data/musics.json", "rb") as f:
        musics_data = json.load(f)
    f.close()

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
                if p != None:
                    message += "\n{0}".format(p)

    return message


def mdbot(qq, message):
    try:
        message_chars = message.split(" ")
        if len(message_chars) == 1:
            return help_message
        if message_chars[1] == "help":
            return help_message
        if message_chars[1] == "update":
            update_musics()
            return "更新完了"
        if message_chars[1] == "bindname":
            success, name = bindname(qq, message_chars[2])
            print(success)
            if success:
                return "就你小子叫{0}({1})啊！".format(name, qq)
            else:
                return "找不到捏，试试用uid绑定"
        if message_chars[1] == "binduid":
            success, name = binduid(qq, message_chars[2])
            if success:
                return "就你小子叫{0}({1})啊！".format(name, qq)
            else:
                return "你这uid有问题啊"
        if message_chars[1] == "unbind":
            success, name = unbind(qq)
            if success:
                return "呜呜呜{0}({1})再见了".format(name, qq)
            else:
                return "找不到捏，可能是没绑，试试/md help"
        if message_chars[1] == "b30":
            success, uid = qq2uid(qq)
            if success:
                return b30(uid)
            else:
                return "找不到捏，可能是没绑，试试/md help"
        if message_chars[1] == "b30name":
            md_name, md_uid, success = name2uid(message_chars[2])
            if md_uid != "":
                return b30(md_uid)
        if message_chars[1] == "dif":
            return level_dif(message_chars[2])
        if message_chars[1] == "song":
            return song_info(message_chars[2])
        if message_chars[1] == "test":
            return "欸嘿！"
        else:
            return "您可真会玩!试试/md help"
    except:
        return "出错了！试试/md help"
