import asyncio
import io
from typing import Dict, List, Tuple

from PIL import Image, ImageDraw, ImageFont

from .utils import url_to_byte


async def b30_image(
    data: List[Tuple[int, Dict[str, str]]],
    master_data: Dict[str, str],
):
    # 创建一个空白模板图像，指定大小和背景颜色
    template_width = 1200  # 模板图像宽度
    template_height = 1200  # 模板图像高度
    template_bg_color = (255, 255, 255)  # 背景颜色（白色）
    template = Image.new("RGB", (template_width, template_height), template_bg_color)
    draw = ImageDraw.Draw(template)
    font_large = ImageFont.truetype("simsun.ttc", 36)
    font_mid = ImageFont.truetype("simsun.ttc", 24)
    ImageFont.truetype("simsun.ttc", 24)
    # 定义每个小图像的大小和间隙大小
    image_width = 128  # 每个小图像的宽度
    image_height = 128  # 每个小图像的高度
    gap = 50  # 图像之间的间隙大小

    # 在模板图像上添加小图像，并留出间隙
    rank = 0

    for i in range(1, 5):  # 行索引
        for j in range(1, 6):  # 列索引
            if (i * 6 + j) < len(data):  # 检查是否还有小图像可以添加
                rank += 1
                _, select_one = data[i * 6 + j]
                image_pic = Image.open(
                    io.BytesIO(await url_to_byte(select_one["pic"])),
                ).resize((128, 128))
                # 测试代码
                # image_pic = Image.open(data[rank][-1]["pic"]).resize((128, 128))

                box = (
                    j * (image_width + gap),
                    i * (image_height + gap),
                    (j * (image_width + gap)) + image_width,
                    i * (image_height + gap) + image_height,
                )
                draw.text(
                    (
                        j * (image_width + gap),
                        i * (image_height + gap) + image_height,
                    ),
                    master_data["name"],
                    font=font_mid,
                    fill="black",
                )
                print(box)
                template.paste(image_pic, box)

    # 选择要使用的字体和字体大小

    # 添加文字
    draw.text((50, 10), master_data["name"], font=font_large, fill="black")
    draw.text((50, 80), master_data["ptt"], font=font_large, fill="black")
    # 保存模板图像
    template.show()
    template.save("template.png")  # 可以根据需要更改保存的文件名和路径
    return template


if __name__ == "__main__":
    data: dict = {}
    master_data = {"uid": "114514", "name": "1919810", "ptt": "ptt"}
    for num in range(1, 31):
        # with open("1.png", mode="rb") as f:
        #     data_img = f.read

        data[num] = (1, {"pic": "1.png"})

    asyncio.run(b30_image(data, master_data))
