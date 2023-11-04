import discord
from discord import app_commands
from index import read_file_content,write_file_content,default_settings,group_template

retweet_command = group_template(name="retweet",description="Change behaviour on links containing retweets.")

@app_commands.checks.has_permissions(manage_guild=True)
@retweet_command.command(name="delete-original-tweet",description="Toggle the deletion of original tweet in the message if present. Off by default.")
async def delete_original_tweet(interaction:discord.Interaction)->None:
    temp_retweet_list=read_file_content("retweet-list",{interaction.guild_id:default_settings["retweet-list"]})
    temp_retweet_list[interaction.guild_id]["delete_original_tweet"]=not temp_retweet_list[interaction.guild_id]["delete_original_tweet"]
    await write_file_content("retweet-list",temp_retweet_list)
    await interaction.response.send_message(f"Toggled the deletion of original tweet, if present in the same message alongside a retweet, {'on.' if temp_retweet_list[interaction.guild_id]['delete_original_tweet']==True else 'off.'}")
    return


async def setup(bot):
    bot.tree.add_command(retweet_command)

async def teardown(bot):
    bot.tree.remove_command("retweet")