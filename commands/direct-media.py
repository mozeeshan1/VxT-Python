import discord
from discord import app_commands
from index import read_file_content,write_file_content,default_settings,group_template
import typing

direct_media_command=group_template(name="direct-media",description="Change behaviour for direct media conversions.")

@app_commands.checks.has_permissions(manage_guild=True)
@direct_media_command.command(name="toggle",description="Toggle the addition of d. subdomain to converted twitter links. Off by default.")
@app_commands.describe(type="The types of tweets to be converted.")
async def toggle(interaction:discord.Interaction,type:typing.Literal["images","videos"])->None:
    temp_dm_list=read_file_content("direct-media-list",{interaction.guild_id:default_settings["direct-media-list"]})
    temp_dm_list[interaction.guild_id]["toggle"][type] = not temp_dm_list[interaction.guild_id]["toggle"][type]
    await write_file_content("direct-media-list",temp_dm_list)
    await interaction.response.send_message(f"Toggled direct media conversion of tweets containing {type} {'on.' if temp_dm_list[interaction.guild_id]['toggle'][type]==True else 'off.'}")
    return


@app_commands.checks.has_permissions(manage_guild=True)
@direct_media_command.command(name="channel",description="Change the permissions for which channels to convert in. All channels by default.")
@app_commands.describe(action="The action to be performed.", channel="The channel to allow or prohibit.")
async def channel_list(interaction:discord.Interaction,action:typing.Literal["list","allow","prohibit","allow all","prohibit all"],channel:typing.Optional[discord.abc.GuildChannel]):
    temp_dm_list=read_file_content("direct-media-list",{interaction.guild_id:default_settings["direct-media-list"]})
    if channel is not None:
        channel=channel.mention
    if action=="list":
        channel_list = temp_dm_list[interaction.guild_id]["channel"]
        
        # Check if all channels are allowed or prohibited
        if "allow" in channel_list or "prohibit" in channel_list:
            await interaction.response.send_message(f"All channels are {'allowed' if 'allow' in channel_list else 'prohibited'}.")
            return
        
        # Generate lists for allowed and prohibited channels
        allowed_list = '\n'.join([f"- {chnl}" for action, chnl in channel_list if action == "allow"])
        prohibited_list = '\n'.join([f"- {chnl}" for action, chnl in channel_list if action == "prohibit"])
        
        await interaction.response.send_message(f"The allowed channels are:\n{allowed_list}\nand the prohibited channels are:\n{prohibited_list}")
        return
    
    # Handle allow and prohibit actions
    elif action in ["allow", "prohibit"]:
        if not channel:
            await interaction.response.send_message("Please select a channel.")
            return
        
        channel_entry = (action, channel)
        channel_list = temp_dm_list[interaction.guild_id]["channel"]
        
        # Check if the channel is already in the list with the same action
        if channel_entry in channel_list or action in channel_list:
            await interaction.response.send_message(f"Direct media conversions in the {channel} channel are already {action}ed.")
            return
        
        # Remove opposite action for the channel if present
        opposite_action = "prohibit" if action == "allow" else "allow"
        channel_list = [item for item in channel_list if item != (opposite_action, channel)]
        
        # Remove general allow/prohibit if present
        if opposite_action in channel_list:
            channel_list.remove(opposite_action)
        
        # Add the new channel entry
        channel_list.append(channel_entry)
        temp_dm_list[interaction.guild_id]["channel"] = channel_list
        
        await write_file_content("direct-media-list", temp_dm_list)
        await interaction.response.send_message(f"Direct media conversions in the {channel} channel will be {action}ed.")
        return

    # Handle allow all and prohibit all actions
    elif action in ["allow all", "prohibit all"]:
        action_key = "allow" if action == "allow all" else "prohibit"
        
        if action_key in temp_dm_list[interaction.guild_id]["channel"]:
            await interaction.response.send_message(f"All channels are already {action_key}ed.")
            return
        
        temp_dm_list[interaction.guild_id]["channel"] = [action_key]
        await write_file_content("direct-media-list", temp_dm_list)
        await interaction.response.send_message(f"Conversions in all channels will be {action_key}ed.")
        return

@app_commands.checks.has_permissions(manage_guild=True)
@direct_media_command.command(name="multiple-images",description="Change the options for tweets with multiple images. Conversion on by default.")
@app_commands.describe(option="Select an option.")
@app_commands.choices(option=[app_commands.Choice(name="convert",value="convert"),app_commands.Choice(name="replace with mosaic",value="replace_with_mosaic")])
async def multiple_images(interaction:discord.Interaction,option:app_commands.Choice[str])->None:
    temp_dm_list=read_file_content("direct-media-list",{interaction.guild_id:default_settings["direct-media-list"]})
    temp_dm_list[interaction.guild_id]["multiple_images"][option.value]=not temp_dm_list[interaction.guild_id]["multiple_images"][option.value]
    temp_response={"convert":f"Direct media conversions for multiple images have been toggled {'on.' if temp_dm_list[interaction.guild_id]['multiple_images']['convert']==True else 'off.'}","replace_with_mosaic":f"Direct media conversions for multiple images will {'be replaced with a mosaic containing all the images.' if temp_dm_list[interaction.guild_id]['multiple_images']['replace_with_mosaic']==True else 'show the first image only.'}{' Note that direct media conversions for multiple images is currently off.' if temp_dm_list[interaction.guild_id]['multiple_images']['convert'] == False else ''}{' Note that direct media conversions for images is currently off.' if temp_dm_list[interaction.guild_id]['toggle']['images'] == False else ''}"}
    await write_file_content("direct-media-list",temp_dm_list)
    await interaction.response.send_message(temp_response[option.value])
    return

@app_commands.checks.has_permissions(manage_guild=True)
@direct_media_command.command(name="quote-tweet",description="Change the options for quote tweet behaviour. Conversion off by default.")
@app_commands.describe(option="Select an option.")
@app_commands.choices(option=[app_commands.Choice(name="convert",value="convert"),app_commands.Choice(name="prefer quoted tweet",value="prefer_quoted_tweet")])
async def quote_tweet(interaction:discord.Interaction,option:app_commands.Choice[str])->None:
    temp_dm_list=read_file_content("direct-media-list",{interaction.guild_id:default_settings["direct-media-list"]})
    temp_dm_list[interaction.guild_id]["quote_tweet"][option.value]=not temp_dm_list[interaction.guild_id]["quote_tweet"][option.value]
    temp_response={"convert":f"Direct media conversions for quote tweets have been toggled {'on.' if temp_dm_list[interaction.guild_id]['quote_tweet']['convert']==True else 'off.'}","prefer_quoted_tweet":f"Direct media conversions for the {'quoted tweet' if temp_dm_list[interaction.guild_id]['quote_tweet']['prefer_quoted_tweet']==True else 'quote tweet'} will be chosen if both have media in them.{' Note that direct media conversions for multiple images is currently off.' if temp_dm_list[interaction.guild_id]['quote_tweet']['convert'] == False else ''}{' Note that direct media conversions for images is currently off.' if temp_dm_list[interaction.guild_id]['toggle']['images'] == False else ''}"}
    await write_file_content("direct-media-list",temp_dm_list)
    await interaction.response.send_message(temp_response[option.value])
    return

async def setup(bot):
    bot.tree.add_command(direct_media_command)


async def teardown(bot):
    bot.tree.remove_command("direct-media")