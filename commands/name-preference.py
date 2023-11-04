import discord
from discord import app_commands
from discord.app_commands import Choice
from index import read_file_content,write_file_content,default_settings

@app_commands.default_permissions(manage_guild=True)
@app_commands.checks.has_permissions(manage_guild=True)
@app_commands.command(name="name-preference", description="Toggle between usernames or display names for users.")
@app_commands.choices(preference=[Choice(name="username",value="username"),Choice(name="display name",value="display name")])
async def name_preference(interaction:discord.Interaction,preference:Choice[str]) -> None:
    temp_name_preference_list = read_file_content("name-preference-list", {interaction.guild_id: default_settings["name-preference-list"]})
    temp_name_preference_list[interaction.guild_id]=preference.value
    await write_file_content("name-preference-list",temp_name_preference_list)
    await interaction.response.send_message(f"Your preference has been updated to {preference.name}.")
    return



async def setup(bot):
    bot.tree.add_command(name_preference)
    
async def teardown(bot):
    bot.tree.remove_command("name-preference")