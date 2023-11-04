import discord
from discord import app_commands
from index import check_if_bot_owner,reload_all_extensions


@app_commands.default_permissions(administrator=True)
@app_commands.check(check_if_bot_owner)
@app_commands.command(name="command-sync", description="Syncs all slash commands. Only available to the owner.")
async def sync(interaction: discord.Interaction) -> None:
    await interaction.response.defer()
    await reload_all_extensions(interaction.client)
    tree_synced=await interaction.client.tree.sync()
    formatted_tree_sync = '\n'.join([f"- {item.name}" for item in tree_synced])
    await interaction.edit_original_response(content=f"The following commands have been synced:\n{formatted_tree_sync}")
    return


async def setup(bot):
    bot.tree.add_command(sync)

async def teardown(bot):
    bot.tree.remove_command("command-sync")