from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Self

import discord
from discord import Interaction, app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from ..bot import Bot


class AlertView(discord.ui.View):
    original_message: discord.Message

    def __init__(self, embed: discord.Embed, original_interaction: discord.Interaction[Bot]) -> None:
        super().__init__()
        self.embed = embed
        self.original_interaction = original_interaction

    @discord.ui.button(label='Click me!', style=discord.ButtonStyle.blurple)
    async def view_alert(self, interaction: discord.Interaction[Bot], button: discord.ui.Button[Self]) -> None:
        await interaction.response.send_message(embed=self.embed, ephemeral=True)

        self.view_alert.disabled = True
        await self.original_message.edit(view=self)
        self.stop()


class InteractionJumpstarter(discord.ui.View):
    interaction: discord.Interaction[Bot]

    @discord.ui.button(label='Click me!', style=discord.ButtonStyle.blurple)
    async def start(self, interaction: discord.Interaction[Bot], button: discord.ui.Button[Self]) -> None:
        self.interaction = interaction
        self.stop()


class ConfirmationView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__()
        self.status = False

    async def end(self, interaction: discord.Interaction[Bot]) -> None:
        for item in self.children:
            if hasattr(item, 'disabled'):
                item.disabled = True

        await interaction.response.edit_message(view=self)
        self.stop()

    @discord.ui.button(label='Looks good!', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction[Bot], button: discord.ui.Button[Self]) -> None:
        self.status = True
        await self.end(interaction)

    @discord.ui.button(label='Ew no', style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction[Bot], button: discord.ui.Button[Self]) -> None:
        self.status = False
        await self.end(interaction)


class AlertEmbedBuilder(discord.ui.Modal, title='Make your embed'):
    title_ = discord.ui.TextInput(label='Title')
    description = discord.ui.TextInput(label='Description', style=discord.TextStyle.paragraph)
    fields = discord.ui.TextInput(
        label='Fields',
        placeholder='First line is name, 2nd is value, etc',
        style=discord.TextStyle.paragraph,
        required=False,
    )
    image_url = discord.ui.TextInput(label='Image URL', required=False)
    expires_in = discord.ui.TextInput(label='Expires in (hours)')

    def __init__(self):
        super().__init__()
        self.view = ConfirmationView()

    def build_embed(self) -> discord.Embed:
        embed = discord.Embed(color=discord.Color.dark_embed())
        embed.set_footer(text='Thank you for supporting us! - Clashlyn dev team😘')

        if self.title_.value:
            embed.title = self.title_.value
        if self.description.value:
            embed.description = self.description.value
        if self.image_url:
            embed.set_image(url=self.image_url.value)

        if self.fields.value:
            iterator = iter(self.fields.value.split('\n'))
            for name in iterator:
                value = next(iterator)
                embed.add_field(name=name, value=value)

        return embed

    async def on_submit(self, interaction: Interaction[Bot]) -> None:
        embed = self.build_embed()
        await interaction.response.send_message(embed=embed, view=self.view, ephemeral=True)
        await self.view.wait()
        self.stop()


class Alerts(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.alerted_users: set[int] = set()
        self.current_alert: discord.Embed | None = None
        self.expires_in: datetime.datetime | None = None

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction: discord.Interaction[Bot], command: app_commands.Command) -> None:
        if self.current_alert is not None and interaction.user.id not in self.alerted_users:
            if discord.utils.utcnow() > self.expires_in:
                self.current_alert = None
                self.expires_in = None
                return

            embed = discord.Embed(
                title='You have been a new alert! Click below to read it!', color=discord.Color.dark_embed()
            )
            view = AlertView(self.current_alert, interaction)
            view.original_message = await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            self.alerted_users.add(interaction.user.id)

    @commands.command()
    @commands.is_owner()
    async def add_alert(self, ctx: commands.Context[Bot]) -> None:
        view = InteractionJumpstarter()
        await ctx.send('Click below to start!', view=view)
        await view.wait()

        modal = AlertEmbedBuilder()
        await view.interaction.response.send_modal(modal)
        await modal.wait()

        if modal.view.status:
            self.current_alert = modal.build_embed()
            await ctx.send('Alert added!')
            self.expires_in = discord.utils.utcnow() + datetime.timedelta(hours=int(modal.expires_in.value))
        else:
            await ctx.send('Alert cancelled :(')


async def setup(bot: Bot) -> None:
    await bot.add_cog(Alerts(bot))
