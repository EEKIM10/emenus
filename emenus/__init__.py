from datetime import datetime

import discord
from discord.ext.menus import Menu, button

DEFAULT_CONF = "Are you sure?\n\n\N{WHITE HEAVY CHECK MARK} Yes!\n\N{CROSS MARK} No."


class Confirm(Menu):
    """
    A menu that returns a simple boolean (True/False), depending on the reaction added.

    The reactions that are added are :white_check_mark: and :x:.
    """
    def __init__(self, description: str = DEFAULT_CONF, *args, **kwargs):
        super().__init__(check_embeds=True, delete_message_after=kwargs.get("delete_message_after", True))
        self.msg = description[:2048]
        self.kwargs = kwargs
        self.res = None

    @button("\N{WHITE HEAVY CHECK MARK}")
    async def on_yes(self, payload: discord.RawReactionActionEvent) -> bool:
        """
        the check mark reaction event. This simply returns True.

        :param payload: provided by the reaction event.
        :return True:
        """
        return True

    @button("\N{CROSS MARK}")
    async def on_no(self, payload: discord.RawReactionActionEvent) -> bool:
        """
        the cross mark reaction event. This simply returns False.

        :param payload: provided by the reaction event.
        :return False:
        """
        return False

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
        await self.start(ctx, channel=chan)
        return self.res