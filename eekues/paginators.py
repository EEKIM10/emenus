import asyncio
from datetime import datetime

import discord
from discord.ext import commands, menus
from . import Selector

__all__ = (
    "EmbedPaginator",
    "ScrollableEmbedPaginator"
)


class EmbedPaginator(commands.Paginator):
    """
    A paginator that just sends everything embedded. Nothing real fancy.

    basically just

    .. codeblock: python
        for page in self.pages:
            await dest.send(embed=discord.Embed(**res_kw, description=page))
    """
    def __init__(self, prefix: str = "", suffix: str = "", *, slow: bool = False, **kwargs):
        super().__init__(prefix=prefix, suffix=suffix, max_size=kwargs.get("p_maxsize", 2048))
        self.prefix = prefix
        self.suffix = suffix
        self.max_size = min(2048, kwargs.get("p_maxsize", 2048))
        self.kwargs = kwargs
        self.slowmode = slow

    def add_page(self, line: str, *, empty: bool = False):
        """
        Adds a new page to the embed.

        Basically a shorthand for self.close_page();self.add_line(...)

        :param empty: same as self.add_line()
        :param line: same as self.add_line()
        :return: None
        """
        self.close_page()
        self.add_line(line, empty=empty)

    async def send(self, ctx: commands.Context, *, destination: discord.abc.Messageable = None) -> [discord.Message]:
        """
        Sends the rendered pages to the desired destination.

        if slow is True, will wait 1 second between sending each embed.

        :param ctx: Take a wild guess
        :param destination: where to send the pages to. Defaults to ctx.channel
        :return: list[discord.Message
        """
        destination = destination or ctx.channel
        messages = []
        res_kw = dict([(x, y) for x, y in self.kwargs if x.lower().startswith("e_") and not x.lower() == "e_description"])
        for page in self.pages:
            e = discord.Embed(description=page, **res_kw)
            await destination.send(embed=e)
            if self.slowmode:
                await asyncio.sleep(1)
            continue
        return messages

    @property
    def embedded_pages(self):
        """Returns the list of pre-rendered embeds"""
        embeds = []
        res_kw = dict([(x, y) for x, y in self.kwargs if x.lower().startswith("e_") and not x.lower() == "e_description"])
        for page in self.pages:
            embeds.append(discord.Embed(description=page, **res_kw))
        return embeds

BASE_N = "\N{variation selector-16}\N{combining enclosing keycap}"
class ScrollableEmbedPaginator(EmbedPaginator, menus.Menu):
    """A reaction-menu based paginator."""

    def _generate_embed(self, embed: discord.Embed):
        embed = self.embedded_pages[self.on]
        embed.set_footer(text=f"Page {self.on + 1}/{len(self.embedded_pages) + 1}")
        embed.timestamp = datetime.utcnow()  # utcnow means the timestamp is localised on discord for each user
        return embed

    def _msg_check(self):
        def pred(m: discord.Message):
            if m.channel != self.message.channel:
                return False
            elif m.author.id not in (self.bot.owner_id, self._author_id):
                return False
            else:
                return True
        return pred

    async def _update(self):
        if self.on > len(self.embedded_pages) - 1:
            self.on -= 1
            return  # no changes needed
        elif self.on < 0:
            self.on = 0
            return  # still no changes needed
        await self.message.edit(embed=self._generate_embed(self.embedded_pages[self.on]))

    async def send_initial_message(self, ctx, channel):
        message = await channel.send(embed=self._generate_embed(self.embedded_pages[self.on]))
        return message

    @menus.button("\U00002b05")  # Left
    async def shift_left(self, payload: discord.RawReactionActionEvent):
        await self.message.remove_reaction(payload.emoji, self.bot.get_user(payload.user_id))
        self.on -= 1
        await self._update()

    @menus.button("\U000023f9") # stop
    async def _stop(self, payload: discord.RawReactionActionEvent):
        await self.message.delete()
        await self.stop()

    @menus.button("\U000027a1")  # Right
    async def shift_right(self, payload: discord.RawReactionActionEvent):
        await self.message.remove_reaction(payload.emoji, self.bot.get_user(payload.user_id))
        self.on += 1
        await self._update()

    @menus.button("\U00000023\U0000fe0f\U000020e3")  # select | #
    async def _select(self, payload: discord.RawReactionActionEvent):
        await self.message.delete()
        items = ["page "+str(n) for n in range(len(self.__pages))]
        page_no = self.pages.index(str(await Selector(items, delete_message_after=True).result(
            self.ctx, self.message.channel))) # AHH IM LOST HOW DOES THIS WORK

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__pages = dict((str(x), y) for x, y in enumerate(self.embedded_pages))
        self._emojis = [str(n) + BASE_N for n in range(10)]
        self.left = "\U00002b05"
        self.right = "\U000027a1"
        self.select = "\U00000023\U0000fe0f\U000020e3"
        self.on = 0
        self.author = self.bot.get_user(self._author_id)