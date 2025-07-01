<!-- markdownlint-disable MD026 MD031 MD033 MD036 MD041 MD046 MD047 MD051 -->
<div align="center">
  <img src="https://raw.githubusercontent.com/Agnes4m/nonebot_plugin_md/main/img/logo.png" width="180" height="180"  alt="AgnesDigitalLogo">
  <br>
  <p><img src="https://s2.loli.net/2022/06/16/xsVUGRrkbn1ljTD.png" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot_plugin_md

_✨游戏慕斯快跑(muse dash)查询✨_

<a href="https://github.com/Agnes4m/nonebot_plugin_md/stargazers">
        <img alt="GitHub stars" src="https://img.shields.io/github/stars/Agnes4m/nonebot_plugin_md" alt="stars">
</a>
<a href="https://github.com/Agnes4m/nonebot_plugin_md/issues">
        <img alt="GitHub issues" src="https://img.shields.io/github/issues/Agnes4m/nonebot_plugin_md" alt="issues">
</a>
<a href="http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=0u2VnosCsDG05IPlQ4SvhCTVLpWqyEqZ&authKey=zEfR1qR358aH4bksKXMwns3nNd1r395ignXLDExp2xG8ENaIzgrAd6%2FRRAo%2B8QR2&noverify=0&group_code=424506063">
        <img src="https://img.shields.io/badge/QQ%E7%BE%A4-424506063-orange?style=flat-square" alt="QQ Chat Group">
</a>
<a href="https://pypi.python.org/pypi/nonebot_plugin_md">
        <img src="https://img.shields.io/pypi/v/nonebot_plugin_md.svg" alt="pypi">

</a>
    <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">
    <img src="https://img.shields.io/badge/nonebot-2.1.0+-red.svg" alt="NoneBot">

</div>

## 说明

使用从MuseDash.moe摸来的数据及api开发的喵斯查分bot，可以实现绑定qq和md账号、查询b30、查询曲目信息、查询难度排行等功能

支持nonebot_plugin_alconna所支持的所有适配器

## 主要功能

- 1. 初始化 发送`md update`
- 2. 绑定 发送`md bindname xxx` 或者 `md binduid xxx`
- 3. b30

## 安装

以下提到的方法 任选**其一** 即可

<details open>
<summary>[推荐] 使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

```bash
nb plugin install nonebot_plugin_md
```

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

```bash
pip install nonebot-plugin-md
```

</details>
<details>
<summary>pdm</summary>

```bash
pdm add nonebot-plugin-md
```

</details>
<details>
<summary>poetry</summary>

```bash
poetry add nonebot-plugin-md
```

</details>
<details>
<summary>conda</summary>

```bash
conda install nonebot-plugin-md
```

</details>
</details>

## 其他

- 本项目原因是几乎找不到开源的md查询插件，因此自己做个开源的，欢迎大佬提iss和pr
- 如果本插件对你有帮助，不要忘了点个Star~
- 本项目仅供学习使用，请勿用于商业用途
- [更新日志](./docs/update.md)
- [AGPL-3.0 License](https://github.com/Agnes4m/nonebot_plugin_md/blob/main/LICENSE) ©[@Agnes4m](https://github.com/Agnes4m)

## 🌐 感谢

- [MDbot](https://github.com/Doctorade/MDBot)- 源代码来源
