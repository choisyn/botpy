# -*- coding: utf-8 -*-
from command_framework import CommandHandler, GroupMessage

# 这个文件包含了常用的、工具性质的指令

# setup 函数，用于将此文件中的指令注册到机器人实例
def setup(bot: CommandHandler):
    @bot.command("帮助")
    async def help_command(message: GroupMessage, *args):
        """
        处理 "帮助" 指令
        """
        txt="\n/帮助: 显示所有可用指令\n/本周更新情况: 查询本周更新日期\n/今日沙雕推荐: 获取今日沙雕推荐内容"
        
        await bot.send_text(message, txt)

    @bot.command("本周更新情况")
    async def ping_command(message: GroupMessage, *args):
        """
        处理 "本周更新情况" 指令
        """
        await bot.send_text(message, "本周暂无更新！")

    @bot.command("今日沙雕推荐")
    async def ping_command(message: GroupMessage, *args):
        """
        处理 "本周更新情况" 指令
        """
        await bot.send_text(message, "今日暂无推荐！")
    @bot.command("信息")
    async def info_command(message: GroupMessage, *args):
        """
        处理 "信息" 指令, 返回消息相关信息
        """
        info_text = (
            f"消息详情：\n"
            f"发送时间: {message.timestamp}\n"
            f"发送用户ID: {message.author.member_openid}\n"
            f"群聊ID: {message.group_openid}"
        )
        await bot.send_text(message, info_text)
