json_path = "data/md_data/players.json"
help_message = """慕斯快跑b30帮助菜单

    /md help呼出此菜单
    /md update:更新曲库及难度表，首次使用需要更新
    /md bindname 名字:使用指定名字账号与当前qq进行绑定，搜索结果不唯一时无法绑定
    /md binduid uid:使用指定uid与当前qq进行绑定\n"
    /md unbind:解除当前qq账号绑定
    /md b30:查询当前qq绑定账号b30
    /md b30name 名字:查询指定名字账号b30，搜索结果不唯一时返回第一个结果
    /md dif 等级:查询指定等级难度排行
    /md song 曲目名称:查询指定歌曲信息，支持模糊匹配
    数据来源：MuseDash.moe
    by AgnesDigital & Nonebot2"""

base_url = "https://musedash.moe"
dif_url = "https://api.musedash.moe/diffdiff"
albums_url = "https://api.musedash.moe/albums"
search_url = "https://api.musedash.moe/search/"
player_url = "https://musedash.moe/player/"
