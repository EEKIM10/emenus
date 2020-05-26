import asyncio

import discord
from discord.ext import commands


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