# -*- coding: utf-8 -*-
import os
from command_framework import CommandHandler, GroupMessage

# 这个文件包含了发送本地媒体文件的指令

# setup 函数，用于将此文件中的指令注册到机器人实例
def setup(bot: CommandHandler):
    @bot.command("图片")
    async def local_image_command(message: GroupMessage, *args):
        """
        处理 "图片" 指令, 发送本地图片和文字
        """
        # 获取当前文件所在目录，并构造图片的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 图片位于 commands 目录的上一级目录下的 image 文件夹中
        image_path = os.path.join(current_dir, "..", "image", "huonv2.jpg")
        
        text_message = "这是图文消息"
        
        await bot.send_local_file_with_text(message, text_message, image_path)
