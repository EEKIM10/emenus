import discord
from discord.ext.menus import Button, MenuError, Menu

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
