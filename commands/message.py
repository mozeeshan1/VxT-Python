import discord
from discord import app_commands
from index import read_file_content,write_file_content,default_settings,group_template

message_command=group_template(name="message",description="Change behaviour of how the bot interacts with messages.")

@app_commands.checks.has_permissions(manage_guild=True)
@message_command.command(name="delete-original",description="Toggle the deleting of the original message. On by default.")
async def delete_original(interaction:discord.Interaction)->None:
    temp_message_list=read_file_content("message-list",{interaction.guild_id:default_settings["message-list"]})
    temp_message_list[interaction.guild_id]["delete_original"]=not temp_message_list[interaction.guild_id]["delete_original"]
    await write_file_content("message-list",temp_message_list)
    await interaction.response.send_message(f"Toggled the deletion of original message {'on.' if temp_message_list[interaction.guild_id]['delete_original']==True else 'off.'}")
    return

@app_commands.checks.has_permissions(manage_guild=True)
@message_command.command(name="other-webhooks",description="Toggle operation on webhooks from other bots. Off by default.")
async def other_webhooks(interaction:discord.Interaction)->None:
    temp_message_list=read_file_content("message-list",{interaction.guild_id:default_settings["message-list"]})
    temp_message_list[interaction.guild_id]["other_webhooks"]=not temp_message_list[interaction.guild_id]["other_webhooks"]
    await write_file_content("message-list",temp_message_list)
    await interaction.response.send_message(f"Toggled operations on webhooks from other bots {'on.' if temp_message_list[interaction.guild_id]['other_webhooks'] == True else 'off.'}")
    return



async def setup(bot):
    bot.tree.add_command(message_command)

async def teardown(bot):
    bot.tree.remove_command("message")