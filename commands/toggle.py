import discord
from discord import app_commands
from index import read_file_content,write_file_content,default_settings
import typing

@app_commands.default_permissions(manage_guild=True)
@app_commands.checks.has_permissions(manage_guild=True)
@app_commands.command(name="toggle",description="Convert links for tweets including the following data. All are converted by default.")
@app_commands.describe(type="The type of tweets.")
async def toggle(interaction:discord.Interaction,type:typing.Literal["text","images","videos","polls","all"])->None:
        temp_toggle_list=read_file_content("toggle-list",{interaction.guild_id:default_settings["toggle-list"]})
        if type == "all":
                # Update all values in existing_dict to new_value
                temp_dict = {key: not temp_toggle_list[interaction.guild_id][type] for key in temp_toggle_list[interaction.guild_id]}
                temp_toggle_list[interaction.guild_id]= temp_dict

        else:
                temp_toggle_list[interaction.guild_id][type]=not temp_toggle_list[interaction.guild_id][type]
        await write_file_content("toggle-list",temp_toggle_list)
        await interaction.response.send_message(f"Toggled all{' '+type if type != 'all' else ''} conversions {'on.' if temp_toggle_list[interaction.guild_id][type] == True else 'off.'}")
        return

async def setup(bot):
        bot.tree.add_command(toggle)

async def teardown(bot):
        bot.tree.remove_command("toggle")