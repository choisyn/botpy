# -*- coding: utf-8 -*-
from command_framework import CommandHandler, GroupMessage

# 这个文件包含了与图片相关的指令

# setup 函数，用于将此文件中的指令注册到机器人实例
def setup(bot: CommandHandler):
    @bot.command("看图")
    async def show_image_command(message: GroupMessage, *args):
        """
        处理 "看图" 指令, 发送网络图片
        """
        image_url = "https://127.0.0.1/usr/uploads/2023/11/1336256765.png?sign=q-sign-algorithm%3Dsha1%26q-ak%3DAKIDfEXm2ndVNXel6IQEtWzJqDQPMCzkS6dN%26q-sign-time%3D1700798900%3B1700802560%26q-key-time%3D1700798900%3B1700802560%26q-header-list%3Dhost%26q-url-param-list%3D%26q-signature%3Dcda36f23b747266da1ec182fb00909a54230a9b7&"
        await bot.send_image(message, image_url)

    @bot.command("看图文")
    async def show_image_with_text_command(message: GroupMessage, *args):
        """
        处理 "看图文" 指令, 发送网络图片和文字
        """
        image_url = "https://127.0.0.1/usr/uploads/2023/11/1336256765.png?sign=q-sign-algorithm%3Dsha1%26q-ak%3DAKIDfEXm2ndVNXel6IQEtWzJqDQPMCzkS6dN%26q-sign-time%3D1700798900%3B1700802560%26q-key-time%3D1700798900%3B1700802560%26q-header-list%3Dhost%26q-url-param-list%3D%26q-signature%3Dcda36f23b747266da1ec182fb00909a54230a9b7&"
        text = "这是一条图文消息。"
        await bot.send_text_with_image(message, text, image_url)
