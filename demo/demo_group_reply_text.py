# -*- coding: utf-8 -*-
import asyncio
import os
import random
import time

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import GroupMessage, Message

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()


class MyClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_group_at_message_create(self, message: GroupMessage):
        msg_time = (int(time.time()*1000)+random.randint(0, 999)) % 1000000000#未来让同时发送多条消息，必须附带不一样的msg_seq参数，这里用时间戳来生成
        messageResult = await message._api.post_group_message(
            group_openid=message.group_openid,
              msg_type=0, 
              msg_id=message.id,
              msg_seq=msg_time,
              content=f"\n收到了消息：{message.content}\n发送时间：{message.timestamp}\n发送者id：{message.author.member_openid}\n群聊id：{message.group_openid}")
        _log.info(messageResult)


if __name__ == "__main__":
    # 通过预设置的类型，设置需要监听的事件通道
    # intents = botpy.Intents.none()
    # intents.public_messages=True

    # 通过kwargs，设置需要监听的事件通道
    intents = botpy.Intents(public_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=test_config["appid"], secret=test_config["secret"])