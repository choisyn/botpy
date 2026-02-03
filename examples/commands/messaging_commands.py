# -*- coding: utf-8 -*-
from command_framework import CommandHandler, GroupMessage

# 这个文件包含了演示不同消息发送方式的指令

# setup 函数，用于将此文件中的指令注册到机器人实例
def setup(bot: CommandHandler):
    @bot.command("分段消息")
    async def multi_message_command(message: GroupMessage, *args):
        """
        处理 "分段消息" 指令, 连续发送两条消息
        """
        await bot.send_text(message, "这是消息A")
        await bot.send_text(message, "这是消息B")
