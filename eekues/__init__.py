import asyncio
import random
from datetime import datetime

import discord
from discord.ext.menus import Menu, button, Button, MenuError

DEFAULT_CONF = "Are you sure?\n\n\N{WHITE HEAVY CHECK MARK} Yes!\n\N{CROSS MARK} No."
DEFAULT_COLORs = {
    "\U0001f534": {"name": "red", "value": 0xdd2e44},
    "\U0001f7e0": {"name": "orange", "value": 0xffac33},
    "\U0001f7e1": {"name": "yellow", "value": 0xfdcb58},
    "\U0001f7e2": {"name": "green", "value": 0x78b159},
    "\U0001f535": {"name": "blue", "value": 0x55acee},
    "\U0001f7e3": {"name": "purple", "value": 0xaa8ed6},
    "\U0001f7e4": {"name": "brown", "value": 0xc1694f},
    "\U000026aa": {"name": "off white", "value": 0xe6e7e8},
    "\U000026ab": {"name": "pretty much black", "value": 0x31373d}
}

__all__ = (
    "Confirm",
    "ColourSelector",
    "ColorSelector"
)


class Confirm(Menu):
    """
    A menu that returns a simple boolean (True/False), depending on the reaction added.

    The reactions that are added are :white_check_mark: and :x:.
    """
    def __init__(self, description: str = DEFAULT_CONF, *args, **kwargs):
        """

        :param description: the description of the embedded message to be sent
        :param args: ignored
        :param kwargs: [...] arguments to pass to discord.Embed()  || delete_message_after [BaseClass Port]
        """
        super().__init__(check_embeds=True, delete_message_after=kwargs.get("delete_message_after", True))
        self.msg = description[:2048]
        self.kwargs = kwargs
        self.res = None

    @button("\N{WHITE HEAVY CHECK MARK}")
    async def on_yes(self, payload: discord.RawReactionActionEvent):
        """
        the check mark reaction event. This simply returns True.

        :param payload: provided by the reaction event.
        :return True:
        """
        if self.bot.get_user(payload.user_id).bot:
            return
        self.res = True
        self.stop()

    @button("\N{CROSS MARK}")
    async def on_no(self, payload: discord.RawReactionActionEvent):
        """
        the cross mark reaction event. This simply returns False.

        :param payload: provided by the reaction event.
        :return False:
        """
        if self.bot.get_user(payload.user_id).bot:
            return
        self.res = False
        self.stop()

    async def send_initial_message(self, ctx, channel):
        title = self.kwargs.get("title", "Are you sure?")
        description = self.msg
        color = self.kwargs.get("color") or self.kwargs.get("colour") or discord.Colour.red()
        timestamp = self.kwargs.get("timestamp", datetime.utcnow())
        e = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=timestamp
        )
        return await channel.send(embed=e)

    async def result(self, ctx, *, channel: discord.abc.Messageable = None) -> bool:
        """Returns the result of the reaction event (True/False)"""
        chan = channel or ctx.channel
        await self.start(ctx, channel=chan, wait=True)
        return self.res


class ColourSelector(Menu):
    """
    Selects from a list of colours that are provided.

    To get custom emojis, you will need to provide the following data structure in the kwarg colo[u]rs:

    {
        "EMOJI_CODEPOINT": {"name": "colour name", "value": 0xHEX_VALUE}
    }

    to get an example, see the DEFAULT_COLORS const in this file.
    """

    def __init__(self, *args, **kwargs):
        """
        :param args: ignored
        :param kwargs: [colours|colors] see class docstring
        """
        super().__init__(*args, **kwargs)
        self.ret = None
        self.emojis = list(kwargs.get("colours", {}).keys()) or list(kwargs.get("colors", {}).keys()) or list(DEFAULT_COLORs.keys())
        self._colours = kwargs.get("colours", {}) or kwargs.get("colors", {}) or DEFAULT_COLORs

    async def callback(self, payload: discord.RawReactionActionEvent):
        if self.bot.get_user(payload.user_id).bot:
            return
        self.ret = self._colours[str(payload.emoji)]
        self.bot.dispatch("colour_picked", self.ret)
        self.stop()

    async def send_initial_message(self, ctx, channel):
        n = ""
        for emoji, colour in self._colours.items():
            n += f"{emoji}: {str(discord.Color(colour['value']))} ({colour['name']})\n"
        e = discord.Embed(
            title="Pick a colour:",
            description=n,
            colour=random.choice([c['value'] for c in self._colours.values()]),
            timestamp=ctx.message.created_at
        )
        e.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url_as(static_format="png"))
        # e.set_footer(text="Please wait until I've added every reaction.", icon_url="https://i.imgur.com/lagdj7g.png")
        msg = await channel.send(embed=e)
        for emoji in self._colours.keys():
            self.add_button(Button(emoji, self.callback))
            await msg.add_reaction(emoji)
        return msg

    async def result(self, ctx) -> discord.Colour:
        """
        Returns the result of the

        :param ctx: the context
        :return:
        """
        await self.start(ctx, wait=True)
        ret = self.ret["value"]
        try:
            return discord.Colour(ret)
        except:
            return self.ret["value"]

ColorSelector = ColourSelector
BASE_N = "\N{variation selector-16}\N{combining enclosing keycap}"

class Selector(Menu):
    """A simple class that returns a number from 0-10"""
    def __init__(self, items: list, **kwargs):
        super().__init__(**kwargs)
        self.kw = kwargs
        self.items = items
        self.numbers = [str(n) + BASE_N for n in range(min(10, len(items)))]
        if len(self.items) > len(self.numbers):
            if len(items) > len(self.numbers) + 2:
                raise MenuError("Tried to initialise SelectorMenu with more than 10 items")
            else:
                self.numbers.append("\N{KEYCAP TEN}")
        self.pairs = []
        for n, v in enumerate(self.items):
            self.pairs.append((self.numbers[n], v))
            self.add_button(Button(self.numbers[n], self._callback, position=n), react=False)
        self.returned = None

    async def _callback(self, payload: discord.RawReactionActionEvent):
        self.returned = self.items[self.numbers.index(str(payload.emoji))]
        self.stop()

    async def send_initial_message(self, ctx, channel):
        e = discord.Embed(
            title=self.kw.get("e_title", "Select one of the following:"),
            description="\n".join([f"{e}: {v}" for e,v in self.pairs]),
            color=discord.Colour.blurple()
        )
        msg = await ctx.sed(embed=e)
        for emoji in self.numbers:
            self.bot.loop.create_task(msg.add_reaction(emoji))
        return msg

    async def result(self, ctx, channel: discord.abc.Messageable = None):
        channel = channel or ctx.channel
        await self.start(ctx, channel=channel, wait=True)
        return self.returned
