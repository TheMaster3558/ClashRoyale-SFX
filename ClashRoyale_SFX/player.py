from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Iterable

import discord

if TYPE_CHECKING:
    from bot import Bot


async def play(interaction: discord.Interaction[Bot], sources: Iterable[os.PathLike[str]]) -> None:
    sources = iter([await discord.FFmpegOpusAudio.from_probe(source, method='fallback') for source in sources])

    def play_next_track(_: Any):
        try:
            source = next(sources)
        except StopIteration:
            return
        else:
            try:
                interaction.guild.voice_client.play(source, after=play_next_track)
            except AttributeError:
                pass
            except discord.ClientException:
                interaction.guild.voice_client.source = source

    play_next_track(None)

    async with interaction.client.session.get(
        f'https://tenor.googleapis.com/v2/search?q=clashroyale+{interaction.command.qualified_name}&key={os.getenv('TENOR_API_KEY')}&client_key={os.getenv('TENOR_CLIENT_KEY')}&limit=1'
    ) as resp:
        data = await resp.json()
    gif_url = data['results'][0]['media_formats']['nanogif']['url']
    embed = discord.Embed(title='Playing!').set_image(url=gif_url)
    await interaction.followup.send(embed=embed)
