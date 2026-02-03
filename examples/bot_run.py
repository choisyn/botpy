# -*- coding: utf-8 -*-
import os
import botpy
from botpy.ext.cog_yaml import read

# 从我们创建的框架文件中导入 CommandHandler 类
from command_framework import CommandHandler

# 读取配置文件
test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

# 设置监听的事件通道
intents = botpy.Intents(public_messages=True)
# 创建机器人实例
bot = CommandHandler(intents=intents)

# --- 加载指令模块 ---

# 自动加载 "examples/commands" 目录下的所有指令
# 注意：路径是相对于你运行机器人的根目录，这里我们假设是从 examples 目录运行
bot.load_commands(os.path.join(os.path.dirname(__file__), "commands"))

# --- 指令加载完成 ---


if __name__ == "__main__":
    try:
        # 运行机器人
        bot.run(appid=test_config["appid"], secret=test_config["secret"])
    except Exception as e:
        print(f"机器人运行出错: {e}")
    finally:
        input("按回车键退出...")
