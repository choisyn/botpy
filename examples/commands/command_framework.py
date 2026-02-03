# -*- coding: utf-8 -*-
import asyncio
import os
import sys
import botpy
import importlib.util
import threading
import http.server
import socketserver
import socket
import time
import random
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import GroupMessage

_log = logging.get_logger()

# --- 辅助函数 ---
def get_local_ip():
    """
    获取本机局域网IP地址
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 连接到一个外部地址（不实际发送数据）
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        _log.warning("无法自动获取局域网IP, 将回退到 127.0.0.1。这可能导致远程服务器无法访问本地文件。")
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# --- 本地文件服务 ---
class FileServer:
    def __init__(self, directory, port=8000):
        self.directory = directory
        self.port = port
        self.httpd = None
        self.server_thread = None

    def start(self):
        # 创建一个知道如何从特定目录提供文件的处理程序
        Handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(
            *args, directory=self.directory, **kwargs
        )
        
        # 解决端口占用问题
        socketserver.TCPServer.allow_reuse_address = True
        self.httpd = socketserver.TCPServer(("", self.port), Handler)
        
        _log.info(f"Starting local file server for '{self.directory}' on port {self.port}")
        self.server_thread = threading.Thread(target=self.httpd.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def stop(self):
        if self.httpd:
            _log.info("Stopping local file server...")
            self.httpd.shutdown()
            self.httpd.server_close()
            self.server_thread.join()
            _log.info("Local file server stopped.")

class CommandHandler(botpy.Client):
    """
    一个简单的命令处理框架
    """
    def __init__(self, intents, **options):
        super().__init__(intents=intents, **options)
        self.commands = {}

    def _get_msg_seq(self):
        """
        生成一个唯一的消息序列号
        """
        return (int(time.time() * 1000) + random.randint(0, 999)) % 1000000000

    def command(self, name):
        """
        一个装饰器，用于注册命令处理函数
        """
        def decorator(func):
            self.commands[name] = func
            _log.info(f"Command '{name}' registered.")
            return func
        return decorator

    def load_commands(self, directory="commands"):
        """
        从指定目录加载命令模块
        """
        _log.info(f"Loading commands from '{directory}'...")

        # 将框架文件所在的目录添加到 sys.path，以确保子模块可以导入它
        framework_dir = os.path.dirname(os.path.abspath(__file__))
        if framework_dir not in sys.path:
            sys.path.insert(0, framework_dir)

        # 确保目录存在
        if not os.path.exists(directory):
            _log.warning(f"Commands directory '{directory}' not found.")
            return
            
        for filename in os.listdir(directory):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                filepath = os.path.join(directory, filename)
                try:
                    # 动态导入模块
                    spec = importlib.util.spec_from_file_location(module_name, filepath)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # 模块需要有一个 setup 函数，用来将命令注册到 bot 实例
                    if hasattr(module, "setup"):
                        module.setup(self)
                        _log.info(f"Successfully loaded commands from {filename}")
                    else:
                        _log.warning(f"No setup function found in {filename}")
                except Exception as e:
                    _log.error(f"Failed to load command module {filename}: {e}")
        
        # 恢复 sys.path (可选，但在复杂应用中是好习惯)
        if framework_dir in sys.path and sys.path[0] == framework_dir:
            sys.path.pop(0)

    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def send_text(self, message: GroupMessage, content: str):
        """发送文本消息"""
        try:
            await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_id=message.id,
                content=content,
                msg_seq=self._get_msg_seq()
            )
        except Exception as e:
            _log.error(f"Error sending text message: {e}")

    async def send_image(self, message: GroupMessage, image_url: str):
        """发送网络图片"""
        try:
            upload_media = await message._api.post_group_file(
                group_openid=message.group_openid,
                file_type=1,  # 1表示图片
                url=image_url
            )
            await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=7,  # 7表示富媒体类型
                msg_id=message.id,
                media=upload_media,
                msg_seq=self._get_msg_seq()
            )
        except Exception as e:
            _log.error(f"Error sending image: {e}")
            await self.send_text(message, "发送图片时出错。")
    
    async def send_text_with_image(self, message: GroupMessage, text: str, image_url: str):
        """发送图文消息"""
        try:
            upload_media = await message._api.post_group_file(
                group_openid=message.group_openid,
                file_type=1,  # 1表示图片
                url=image_url
            )
            await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=7,  # 7表示富媒体类型
                msg_id=message.id,
                media=upload_media,
                content=text,
                msg_seq=self._get_msg_seq()
            )
        except Exception as e:
            _log.error(f"Error sending text with image: {e}")
            await self.send_text(message, "发送图文消息时出错。")

    async def send_local_file_with_text(self, message: GroupMessage, text: str, file_path: str):
        """
        通过启动本地HTTP服务来发送本地文件（图片等）并附带消息
        """
        # 检查文件是否存在
        if not os.path.exists(file_path):
            _log.error(f"Local file not found at path: {file_path}")
            await self.send_text(message, f"错误：找不到文件 {os.path.basename(file_path)}")
            return
        
        # 从文件路径中获取目录和文件名
        file_dir = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)

        # 启动本地文件服务
        # 自动获取局域网IP。
        # !!! 警告 !!!
        # 机器人API服务器需要能通过这个IP和端口访问到你的电脑。
        # 如果你的电脑在路由器后面，你需要在路由器上设置【端口转发】
        # 将外部网络的 8000 端口请求，转发到这台电脑的IP的 8000 端口。
        # 否则，API服务器将无法下载文件，导致发送失败。
        server_ip = get_local_ip()
        server_port = 8000
        server = FileServer(directory=file_dir, port=server_port)
        server.start()

        try:
            # 构建文件的URL
            file_url = f"http://{server_ip}:{server_port}/{file_name}"
            _log.info(f"Generated local file URL: {file_url}")
            
            # 使用 send_text_with_image 发送这个URL
            await self.send_text_with_image(message, text, file_url)

        finally:
            # 确保服务被关闭
            server.stop()

    async def on_group_at_message_create(self, message: GroupMessage):
        """
        处理群 @ 消息事件
        """
        content = message.content.strip()
        
        # 清理消息内容，移除开头的 @机器人 和可能的多余空格
        # botpy 会自动移除@信息，但我们还是额外处理一下
        if content.startswith(f"<@!{self.robot.id}>"):
             content = content.replace(f"<@!{self.robot.id}>", "").strip()

        if not content:
            return

        # 先处理可选的 / 前缀，再分割指令，这样更健壮
        if content.startswith('/'):
            content = content[1:].lstrip()  # 移除 / 和后续的空格

        # 如果消息只包含 / 或者 / 后全是空格，则直接返回
        if not content:
            return

        parts = content.split()
        command_name = parts[0]
        args = parts[1:]

        if command_name in self.commands:
            _log.info(f"Executing command '{command_name}' with args: {args}")
            try:
                # 调用注册的命令处理函数
                await self.commands[command_name](message, *args)
            except Exception as e:
                _log.error(f"Error executing command '{command_name}': {e}")
                await self.send_text(message, f"执行命令 {command_name} 时出错。")

if __name__ == "__main__":
    # 读取配置文件
    test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

    # 设置监听的事件通道
    intents = botpy.Intents(public_messages=True)
    bot = CommandHandler(intents=intents)

    # 注册一个简单的 "hello" 命令
    @bot.command("hello")
    async def hello_command(message: GroupMessage, *args):
        """
        处理 hello 命令
        """
        await bot.send_text(message, f"你好, {message.author.member_openid}! 我收到了你的 hello 命令。")

    # 注册一个 "echo" 命令，重复用户发送的消息
    @bot.command("echo")
    async def echo_command(message: GroupMessage, *args):
        """
        处理 echo 命令
        """
        echo_message = " ".join(args)
        if not echo_message:
            echo_message = "你没有提供任何内容让我复述！"
        
        await bot.send_text(message, echo_message)

    # 注册一个 "image" 命令，发送一张图片
    @bot.command("image")
    async def image_command(message: GroupMessage, *args):
        """
        处理 image 命令, 发送网络图片
        """
        file_url = "https://127.0.0.1/PK1%20VIP%E7%BB%8F%E9%AA%8C%E8%A1%A8.png"  # 示例图片URL
        await bot.send_image(message, file_url)
    
    # 注册一个 "text_with_image" 命令，发送图文消息
    @bot.command("text_with_image")
    async def text_with_image_command(message: GroupMessage, *args):
        """
        处理 text_with_image 命令, 发送图文消息
        """
        text_content = " ".join(args)
        if not text_content:
            text_content = "这是一条图文消息！"

        file_url = "https://qqbot.qq.com/wiki/static/wiki/icons/android-chrome-512x512.png" # 示例图片URL
        await bot.send_text_with_image(message, text_content, file_url)

    # 运行机器人
    bot.run(appid=test_config["appid"], secret=test_config["secret"])
