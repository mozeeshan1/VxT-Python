import discord
from discord import app_commands
from index import read_file_content,write_file_content,default_settings,group_template
import typing

webhooks_command=group_template(name="webhooks",description="Change settings for usage of webhooks.")

@app_commands.default_permissions(manage_guild=True)
@app_commands.checks.has_permissions(manage_guild=True)
@webhooks_command.command(name="preference",description="Choose between webhooks and the bot for link conversions. Webhooks are used by default.")
@app_commands.describe(option="The option")
async def preference(interaction:discord.Interaction,option:typing.Literal["webhooks","bot"])->None:
        temp_webhook_list=read_file_content("webhook-list",{interaction.guild_id:default_settings["webhook-list"]})
        temp_webhook_list[interaction.guild_id]["preference"]=option
        await write_file_content("webhook-list",temp_webhook_list)
        await interaction.response.send_message(f"The preference has been updated to use {option} for the conversion of links.")
        return


@app_commands.checks.has_permissions(manage_guild=True)
@webhooks_command.command(name="reply",description="Toggle whether the conversions are replied to the original message or not. Off by default.")
async def reply(interaction:discord.Interaction)->None:
        temp_webhook_list=read_file_content("webhook-list",{interaction.guild_id:default_settings["webhook-list"]})
        temp_webhook_list[interaction.guild_id]["reply"]=not temp_webhook_list[interaction.guild_id]["reply"]
        await write_file_content("webhook-list",temp_webhook_list)
        await interaction.response.send_message(f"Toggled replying to original message {'on.' if temp_webhook_list[interaction.guild_id]['reply'] == True else 'off.'} Please note that reply will only work for bot messages and not webhooks.")
        return

async def setup(bot):
        bot.tree.add_command(webhooks_command)

async def teardown(bot):
        bot.tree.remove_command("webhooks")