import discord
from discord import app_commands



@app_commands.command(name="ping", description="replies with pong")
async def ping(interaction: discord.Interaction) -> None:
    await interaction.response.send_message("Pong")
    # raise ValueError("ping error")
    return


async def setup(bot):
    bot.tree.add_command(ping)


async def teardown(bot):
    bot.tree.remove_command("ping")
