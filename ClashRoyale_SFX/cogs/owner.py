from __future__ import annotations

from typing import TYPE_CHECKING, Self, Type

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from ..bot import Bot


class EditResponseModal(discord.ui.Modal):
    async def on_submit(self, interaction: discord.Interaction[Bot]) -> None:
        await interaction.response.defer()


class StatusView(discord.ui.View):
    message: discord.Message

    def __init__(self) -> None:
        super().__init__()

        self.activity_type: Type[discord.BaseActivity] | None = None
        self.status: str | None = None
        self.url: str | None = None

    def revise_embed(self) -> discord.Embed:
        return (
            discord.Embed()
            .add_field(name='Activity Type', value=self.activity_type and self.activity_type.__name__)
            .add_field(name='Status', value=self.status)
            .add_field(name='URL', value=self.url)
        )

    @discord.ui.select(
        options=[
            discord.SelectOption(label=activity_type.__name__)
            for activity_type in (discord.Game, discord.Streaming, discord.CustomActivity)
        ]
    )
    async def select_activity_type(self, interaction: discord.Interaction[Bot], select: discord.ui.Select[Self]) -> None:
        self.activity_type = getattr(discord, select.values[0])
        if self.activity_type is discord.Streaming:
            self.add_url.disabled = False
        else:
            self.add_url.disabled = True
            self.url = None

        await interaction.response.edit_message(embed=self.revise_embed(), view=self)

    @discord.ui.button(label='Add status')
    async def add_name(self, interaction: discord.Interaction[Bot], button: discord.ui.Button[Self]) -> None:
        text_input = discord.ui.TextInput(label='Status')
        modal = EditResponseModal(title='Add status').add_item(text_input)

        await interaction.response.send_modal(modal)
        await modal.wait()
        self.status = text_input.value

        await self.message.edit(embed=self.revise_embed(), view=self)

    @discord.ui.button(label='Add URL', disabled=True)
    async def add_url(self, interaction: discord.Interaction[Bot], button: discord.ui.Button[Self]) -> None:
        text_input = discord.ui.TextInput(label='URL')
        modal = EditResponseModal(title='Add URL').add_item(text_input)

        await interaction.response.send_modal(modal)
        await modal.wait()
        self.url = text_input.value

        await self.message.edit(embed=self.revise_embed(), view=self)

    @discord.ui.button(label='Done', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction[Bot], button: discord.ui.Button[Self]) -> None:
        for item in self.children:
            if hasattr(item, 'disabled'):
                item.disabled = True

        await interaction.response.edit_message(view=self)
        self.stop()


class Owner(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @commands.command()
    async def status(self, ctx: commands.Context[Bot]) -> None:
        view = StatusView()
        view.message = await ctx.send(view=view)
        await view.wait()

        kwargs = {'name': view.status}
        if view.url is not None:
            kwargs['url'] = view.url

        await self.bot.change_presence(activity=view.activity_type(**kwargs))


async def setup(bot: Bot) -> None:
    await bot.add_cog(Owner(bot))
