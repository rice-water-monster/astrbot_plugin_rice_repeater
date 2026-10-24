"""米饭复读机 —— 一只只会喊「米饭呢」的蓝色大肥鱼。

指令：
    /米饭        回一句米饭相关话术
    /抽象        回一句抽象话术
    /喂饭 <内容>  记录一句自定义复读素材（内存态，重启即忘）
"""

from __future__ import annotations

import random

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register

RICE_LINES = [
    "米饭呢？",
    "先喂我一口。",
    "🍚 拿来。",
    "饭呢？我问你饭呢？",
    "别水了，干饭。",
    "你这话吧友看了都得笑，先吃饭。",
]

ABSTRACT_LINES = [
    "啊？",
    "然后呢？",
    "所以呢？",
    "你是真逆天。",
    "笑了。",
    "你先别急。",
    "别来沾边，退退退。",
    "我一直都在好好说话啊。",
]

DEFAULT_KEYWORDS = ("米饭", "干饭", "饿了")


@register(
    "astrbot_plugin_rice_repeater",
    "吧务删我我还发",
    "米饭复读机：饿了就喊，喊了就复读",
    "0.1.0",
)
class RiceRepeater(Star):
    def __init__(self, context: Context, config: dict | None = None):
        super().__init__(context)
        config = config or {}
        self.passive_enable = bool(config.get("passive_enable", False))
        try:
            self.passive_probability = float(config.get("passive_probability", 0.05))
        except (TypeError, ValueError):
            self.passive_probability = 0.05
        keywords = config.get("passive_keywords") or DEFAULT_KEYWORDS
        self.keywords = tuple(str(k) for k in keywords if str(k).strip())
        self.extra_lines: list[str] = []
        logger.info(
            f"[米饭复读机] 已加载，passive={self.passive_enable}, "
            f"p={self.passive_probability}, keywords={self.keywords}"
        )

    @filter.command("米饭")
    async def rice(self, event: AstrMessageEvent):
        """喊一声就有饭。"""
        yield event.plain_result(random.choice(RICE_LINES))

    @filter.command("抽象")
    async def abstract(self, event: AstrMessageEvent):
        """随机输出一句抽象话术。"""
        pool = self.extra_lines + ABSTRACT_LINES
        yield event.plain_result(random.choice(pool))

    @filter.command("喂饭")
    async def feed(self, event: AstrMessageEvent, text: str = ""):
        """投喂自定义复读素材。"""
        text = (text or "").strip()
        if not text:
            yield event.plain_result("啊？喂空气呢？说点人话。")
            return
        self.extra_lines.append(text[:100])
        if len(self.extra_lines) > 50:
            self.extra_lines.pop(0)
        yield event.plain_result(f"收了，以后我就复读这句：「{text}」。米饭呢？")

    @filter.event_message_type(filter.EventMessageType.ALL)
    async def passive_repeat(self, event: AstrMessageEvent):
        """被动复读：命中关键词时按概率冒一句。"""
        if not self.passive_enable:
            return
        message = (event.message_str or "").strip()
        if not message or not any(k in message for k in self.keywords):
            return
        if random.random() > self.passive_probability:
            return
        pool = self.extra_lines + RICE_LINES + ABSTRACT_LINES
        yield event.plain_result(random.choice(pool))
