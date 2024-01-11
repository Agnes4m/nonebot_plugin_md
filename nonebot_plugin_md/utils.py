import aiohttp

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0",  # noqa: E501
}


async def url_to_byte(url: str):
    """获取URL数据的字节流"""

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=600) as response:
            if response.status == 200:
                return await response.read()
            return None


async def url_to_msg(url: str):
    """获取URL数据的字节流"""

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=600) as response:
            if response.status == 200:
                return await response.text()
            return None
