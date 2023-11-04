import discord
from discord import app_commands
from index import read_file_content,write_file_content,default_settings,group_template

delete_bot_message_command=group_template(name="delete-bot-message",description="Change the behaviour of deletion of bots converted tweets.")

@app_commands.checks.has_permissions(manage_guild=True)
@delete_bot_message_command.command(name="toggle",description="Toggle the ability to delete bot messages with reactions. Off by default.")
async def toggle(interaction:discord.Interaction)->None:
    temp_del_bot_list=read_file_content("delete-bot-message-list",{interaction.guild_id:default_settings["delete-bot-message-list"]})
    temp_del_bot_list[interaction.guild_id]["toggle"]=not temp_del_bot_list[interaction.guild_id]["toggle"]
    await write_file_content("delete-bot-message-list",temp_del_bot_list)
    await interaction.response.send_message(f"Deletion of converted links using reactions has been turned {'on.' if temp_del_bot_list[interaction.guild_id]['toggle'] else 'off.'}")
    return

@app_commands.checks.has_permissions(manage_guild=True)
@delete_bot_message_command.command(name="number",description="Change the number of reactions required to delete bot messages. 1 by default.")
@app_commands.describe(number="The number of reactions required.")
async def numb(interaction:discord.Interaction,number:app_commands.Range[int,0])->None:
    temp_del_bot_list=read_file_content("delete-bot-message-list",{interaction.guild_id:default_settings["delete-bot-message-list"]})
    temp_del_bot_list[interaction.guild_id]["number"]=number
    await write_file_content("delete-bot-message-list",temp_del_bot_list)
    await interaction.response.send_message(f"The number of reactions required to delete the bot message has been changed to: {number}")
    return

async def setup(bot):
    bot.tree.add_command(delete_bot_message_command)

async def teardown(bot):
    bot.tree.remove_command("delete-bot-message")