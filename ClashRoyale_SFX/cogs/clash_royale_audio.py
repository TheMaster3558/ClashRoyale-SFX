from __future__ import annotations

import random
from typing import TYPE_CHECKING, Literal

import discord
from discord import app_commands
from discord.ext import commands

from .votes import AllView, NoMoreCommands
from ..player import play

if TYPE_CHECKING:
    from ..bot import Bot


@app_commands.check
async def check_commands_remaining(interaction: discord.Interaction) -> bool:
    bot: Bot = interaction.client

    bot.commands_remaining.setdefault(interaction.user.id, 10)
    if bot.commands_remaining[interaction.user.id] <= 0:
        raise NoMoreCommands()

    bot.commands_remaining[interaction.user.id] -= 1
    return True


class ClashRoyaleAudio(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @app_commands.command(description='Clash Royale battle music!')
    @app_commands.rename(_8bit='8bit')
    @check_commands_remaining
    async def battle(
        self,
        interaction: discord.Interaction[Bot],
        sudden_death: bool = False,
        boat_battle: bool = False,
        result: Literal['win', 'loss', 'draw'] = 'win',
        _8bit: bool = False,
        training_camp: bool = False,
    ) -> None:
        if _8bit and training_camp:
            embed = discord.Embed(
                title='That\'s not how it works',
                description='You can\'t have both 8bit and training camp',
                color=discord.Color.dark_embed(),
            )
            await interaction.followup.send(embed=embed)
            return

        if _8bit:
            sources = ['audio/clash_royale/battle/2min_loop_battle_8bit.ogg']
        elif training_camp:
            sources = ['audio/battle/Tutorial_2m_arena_forest_amb_01.ogg']
        else:
            sources = [
                random.choice(
                    [
                        'audio/clash_royale/battle/2min_loop_battle_01.ogg',
                        'audio/clash_royale/battle/2min_loop_battle_02.ogg',
                        'audio/clash_royale/battle/2min_loop_battle_03.ogg',
                    ]
                )
            ]

        if training_camp:
            sources.append('audio/clash_royale/battle/60secs_training_Arena_01.ogg')
        else:
            if boat_battle:
                sources.extend(
                    [
                        'audio/clash_royale/battle/Boat_bonus_60sec_01.ogg',
                        'audio/clash_royale/battle/Boat_bonus_30sec_01.ogg',
                    ]
                )
            else:
                sources.extend(
                    [
                        'audio/clash_royale/battle/60_sec_music_loop_01.ogg',
                        'audio/clash_royale/battle/30_sec_music_loop_01.ogg',
                    ]
                )
            sources.append('audio/clash_royale/battle/10_sec_music_loop_01.mp3.mpeg')
        if sudden_death:
            sources.append(
                'audio/clash_royale/battle/Sudden_death_8bit.ogg'
                if _8bit
                else 'audio/clash_royale/battle/Sudden_death_02.ogg'
            )
            sources.append(
                'audio/clash_royale/battle/Sudden_death_8bit.ogg'
                if _8bit
                else 'audio/clash_royale/battle/Sudden_death_02.ogg'
            )

        sources.append('audio/clash_royale/battle/Scroll_preresult_loop_01.ogg')
        if boat_battle:
            match result:
                case 'win':
                    sources.append('audio/clash_royale/battle/Boat_pve_win_01.ogg')
                case 'loss':
                    sources.append('audio/clash_royale/battle/Boat_pve_lose_01.ogg')
                case 'draw':
                    embed = discord.Embed(
                        title='Do you even play clash?',
                        description='You can\'t have a draw in boat battles',
                        color=discord.Color.dark_embed(),
                    )
                    await interaction.followup.send(embed=embed)
                    return
        else:
            match result:
                case 'win':
                    sources.append('audio/clash_royale/battle/Scroll_win_02.ogg')
                case 'loss':
                    sources.append('audio/clash_royale/battle/Scroll_lose_01.ogg')
                case 'draw':
                    sources.append('audio/clash_royale/battle/Scroll_draw_01.ogg')
        sources.append('audio/clash_royale/battle/Scroll_post_jingle_loop_01.ogg')

        if await self.bot.join_command.callback(self, interaction):
            await play(interaction, sources)

    @app_commands.command(description='Clash Royale menu music!')
    @app_commands.rename(_8bit='8bit')
    @check_commands_remaining
    async def menu(self, interaction: discord.Interaction[Bot], _8bit: bool = False) -> None:
        source = (
            'audio/clash_royale/menu/Royale_8bit_menu.ogg'
            if _8bit
            else random.choice(
                [
                    'audio/clash_royale/menu/Menu_03.ogg',
                    'audio/clash_royale/menu/New_menu_01.ogg',
                    'audio/clash_royale/menu/Wizmen04.ogg',
                ]
            )
        )

        if await self.bot.join_command.callback(self, interaction):
            await play(interaction, [source])

    @app_commands.command(description='Electricity!')
    @check_commands_remaining
    async def electro_wizard(self, interaction: discord.Interaction[Bot]) -> None:
        source = random.choice(
            [
                f'audio/clash_royale/cards/electro_wizard/ELECTRO WIZ ATK 0{i} - AUDIO FROM JAYUZUMI.COM.mp3'
                for i in range(1, 6)
            ]
        )
        if await self.bot.join_command.callback(self, interaction):
            await play(interaction, [source])

    @app_commands.command(description='HOG RIIIIIIDER')
    @check_commands_remaining
    async def hog_rider(self, interaction: discord.Interaction[Bot]) -> None:
        source = 'audio/clash_royale/cards/hog_rider/hog_rider.mp3'
        if await self.bot.join_command.callback(self, interaction):
            await play(interaction, [source])

    @app_commands.command(description='HEHEHEHA!')
    @check_commands_remaining
    async def heheheha(self, interaction: discord.Interaction[Bot]) -> None:
        source = 'audio/clash_royale/king/heheheha.mp3'
        if await self.bot.join_command.callback(self, interaction):
            await play(interaction, [source])

    king = app_commands.Group(name='king', description='OG King emotes!')

    @king.command(description='Thumbs up!')
    @check_commands_remaining
    async def congrats(self, interaction: discord.Interaction[Bot]) -> None:
        source = random.choice([f'audio/clash_royale/king/king_congrats_0{i}.ogg' for i in range(1, 5)])
        if await self.bot.join_command.callback(self, interaction):
            await play(interaction, [source])

    @king.command(description='mewmewmewmewmew')
    @check_commands_remaining
    async def cry(self, interaction: discord.Interaction[Bot]) -> None:
        source = random.choice([f'audio/clash_royale/king/king_crying_0{i}.ogg' for i in range(1, 5)])
        if await self.bot.join_command.callback(self, interaction):
            await play(interaction, [source])

    @king.command(description='HAPPY!')
    @check_commands_remaining
    async def happy(self, interaction: discord.Interaction[Bot]) -> None:
        source = random.choice([f'audio/clash_royale/king/king_happy_0{i}.ogg' for i in range(1, 5)])
        if await self.bot.join_command.callback(self, interaction):
            await play(interaction, [source])

    @king.command(description='HEHEHEHA!')
    @check_commands_remaining
    async def laugh(self, interaction: discord.Interaction[Bot]) -> None:
        source = random.choice([f'audio/clash_royale/king/king_laughter_0{i}.ogg' for i in range(1, 5)])
        if await self.bot.join_command.callback(self, interaction):
            await play(interaction, [source])

    @king.command(description='GRRRRR!')
    @check_commands_remaining
    async def mad(self, interaction: discord.Interaction[Bot]) -> None:
        source = random.choice([f'audio/clash_royale/king/king_mad_0{i}.ogg' for i in range(1, 5)])
        if await self.bot.join_command.callback(self, interaction):
            await play(interaction, [source])

    @app_commands.command(description='Most toxic emote fr')
    @check_commands_remaining
    async def goblin(self, interaction: discord.Interaction[Bot]) -> None:
        source = 'audio/clash_royale/cards/goblin/goblin-laugh-clash-royale.mp3'
        if await self.bot.join_command.callback(self, interaction):
            await play(interaction, [source])

    @app_commands.command(description='Bock Bock')
    @check_commands_remaining
    async def chicken(self, interaction: discord.Interaction[Bot]) -> None:
        source = 'audio/clash_royale/chicken/chicken-emote-clash-royale.mp3'
        if await self.bot.join_command.callback(self, interaction):
            await play(interaction, [source])


async def setup(bot: Bot) -> None:
    cog = ClashRoyaleAudio(bot)
    await bot.add_cog(cog)
