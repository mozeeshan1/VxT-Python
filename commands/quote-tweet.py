import discord
from discord import app_commands
from index import read_file_content, write_file_content, default_settings, group_template
import typing

quote_tweet_command = group_template(
    name="quote-tweet", description="Change behaviour for quote tweets.")


@app_commands.checks.has_permissions(manage_guild=True)
@quote_tweet_command.command(name="link-conversion", description="Convert quote tweets including these types of data. Follows the behaviour of the tweets by default.")
@app_commands.describe(type="The type of tweets.")
async def link_conversion(interaction: discord.Interaction, type: typing.Literal["text", "images", "videos", "polls", "all", "follow tweets"]) -> None:
    temp_quote_tweet_list = read_file_content(
        "quote-tweet-list", {interaction.guild_id: default_settings["quote-tweet-list"]})
    # Check if the type is 'all'
    if type == 'all':
        # Determine the new value based on the current state of 'all'
        new_value = not temp_quote_tweet_list[interaction.guild_id]["link_conversion"][type]
        # Set the new value for text, images, videos, polls, and all
        for key in ['text', 'images', 'videos', 'polls', 'all']:
            temp_quote_tweet_list[interaction.guild_id]["link_conversion"][key] = new_value
        # Turn off follow tweets if 'all' is being toggled
        temp_quote_tweet_list[interaction.guild_id]["link_conversion"]['follow tweets'] = False
    else:
        # Toggle the specific type
        temp_quote_tweet_list[interaction.guild_id]["link_conversion"][type] = not temp_quote_tweet_list[interaction.guild_id]["link_conversion"][type]
    
    await write_file_content("quote-tweet-list", temp_quote_tweet_list)
    await interaction.response.send_message(f"Toggled {type} {'settings' if type == 'follow tweets' else 'conversions'} {'on.' if temp_quote_tweet_list[interaction.guild_id]['link_conversion'][type] == True else 'off.'}{' Note that follow tweets settings is on and will take precedence over other custom settings' if temp_quote_tweet_list[interaction.guild_id]['link_conversion']['follow tweets'] == True and type != 'follow tweets' else ''}")
    return


@app_commands.checks.has_permissions(manage_guild=True)
@quote_tweet_command.command(name="remove-quoted-tweet", description="Toggle the removal of the quoted tweet in the message if present. Off by default.")
async def remove_quoted_tweet(interaction: discord.Interaction) -> None:
    temp_quote_tweet_list = read_file_content(
        "quote-tweet-list", {interaction.guild_id: default_settings["quote-tweet-list"]})
    temp_quote_tweet_list[interaction.guild_id]["remove quoted tweet"] = not temp_quote_tweet_list[interaction.guild_id]["remove quoted tweet"]
    await write_file_content("quote-tweet-list", temp_quote_tweet_list)
    await interaction.response.send_message(f"Toggled the deletion of quoted tweet, if present, {'on.' if temp_quote_tweet_list[interaction.guild_id]['remove quoted tweet'] == True else 'off.'}")
    return


async def setup(bot):
    bot.tree.add_command(quote_tweet_command)

async def teardown(bot):
    bot.tree.remove_command("quote-tweet")
