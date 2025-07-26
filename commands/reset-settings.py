import discord
from discord import app_commands
from index import read_file_content,write_file_content,default_settings
import os


class reset_buttons(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(style=discord.ButtonStyle.primary,label="Confirm")
    async def confirmButton(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.defer(ephemeral=True) 
        await interaction.edit_original_response(content="⏳  Resetting all settings…",view=None)
        for filename in default_settings.keys():
            temp_list=read_file_content(filename,{interaction.guild_id:default_settings[filename]})
            temp_list[interaction.guild_id]=default_settings[filename]
            await write_file_content(filename,temp_list)
        await interaction.edit_original_response(content="Successfully reset all settings.")
        self.stop()
        return
    
    @discord.ui.button(style=discord.ButtonStyle.danger,label="Cancel")
    async def cancelButton(self,interaction:discord.Interaction,button:discord.ui.Button):
        await interaction.response.edit_message(content="Settings have not been reset.", view=None)
        self.stop()
        return
        

@app_commands.default_permissions(manage_guild=True)
@app_commands.checks.has_permissions(manage_guild=True)
@app_commands.command(name="reset-settings",description="Reset all settings to default settings.")
async def reset(interaction:discord.Interaction) -> None:
    await interaction.response.send_message("Are you sure you want to reset all settings?", view=reset_buttons(),ephemeral=True)
    return


async def setup(bot):
    bot.tree.add_command(reset)

async def teardown(bot):
    bot.tree.remove_command("reset-settings")