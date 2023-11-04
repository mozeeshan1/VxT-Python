import discord
from discord import app_commands
from index import read_file_content, write_file_content, default_settings, group_template
import typing

mention_command = group_template(
    name="mention", description="Add or remove mentions to ignore.")



@app_commands.checks.has_permissions(manage_guild=True)
@mention_command.command(name="remove", description="Perform actions on the remove list.")
@app_commands.describe(action="The action to be performed.", mention_object="The mention you want to add or remove. Does nothing for other options.")
@app_commands.rename(mention_object="mention")
async def remove(interaction: discord.Interaction, action: typing.Literal["add", "remove", "list", "clear"], mention_object: typing.Optional[discord.User | discord.Role]) -> None:
    temp_mention_list = read_file_content(
        "mention-remove-list", {interaction.guild_id: default_settings["mention-remove-list"]})
    if action == "add":
        if mention_object == None:
            await interaction.response.send_message(f"Please select a mention to add.")
            return
        elif mention_object.mention in temp_mention_list[interaction.guild_id] or (mention_object.name == "@everyone" and "everyone" in temp_mention_list[interaction.guild_id]):
            await interaction.response.send_message(f"The mention {mention_object.name if mention_object.name == '@everyone' else mention_object.mention} already exists.", allowed_mentions=discord.AllowedMentions.none())
            return
        temp_mention_list[interaction.guild_id].add(
            "everyone") if mention_object.name == "@everyone" else temp_mention_list[interaction.guild_id].add(mention_object.mention)
        await write_file_content("mention-remove-list", temp_mention_list)
        await interaction.response.send_message(f"The mention {mention_object.name if mention_object.name == '@everyone' else mention_object.mention} has been added to the list.", allowed_mentions=discord.AllowedMentions.none())
        return
    elif action == "remove":
        if mention_object == None:
            await interaction.response.send_message(f"Please select a mention to remove.")
            return
        elif mention_object.mention in temp_mention_list[interaction.guild_id] or "everyone" in temp_mention_list[interaction.guild_id]:
            temp_mention_list[interaction.guild_id].remove(
                "everyone") if mention_object.name == "@everyone" else temp_mention_list[interaction.guild_id].remove(mention_object.mention)
            await write_file_content("mention-remove-list", temp_mention_list)
            await interaction.response.send_message(f"The mention {mention_object.name if mention_object.name == '@everyone' else mention_object.mention} has been removed from the list.", allowed_mentions=discord.AllowedMentions.none())
            return
        await interaction.response.send_message(f"The mention {mention_object.name if mention_object.name == '@everyone' else mention_object.mention} does not exist in the list. Please use the add option to add it.", allowed_mentions=discord.AllowedMentions.none())
        return
    elif action == "list":
        if len(temp_mention_list[interaction.guild_id]) == 0:
            await interaction.response.send_message(f"There are no mentions registered for this server. Use the add option to add some.")
            return
        formatted_list = "\n".join(
            [f"- @everyone\n- @here" if item == "everyone" else f"- {item}" for item in temp_mention_list[interaction.guild_id]])
        await interaction.response.send_message(f"The mentions in the list are:\n{formatted_list}", allowed_mentions=discord.AllowedMentions.none())
        return
    elif action == "clear":
        if len(temp_mention_list[interaction.guild_id]) == 0:
            await interaction.response.send_message(f"The list is already empty. Please use the add option to add mentions.")
            return
        temp_mention_list[interaction.guild_id].clear()
        await write_file_content("mention-remove-list", temp_mention_list)
        await interaction.response.send_message(f"All mentions have been removed from the list.")
        return
    return



@app_commands.checks.has_permissions(manage_guild=True)
@mention_command.command(name="remove-all", description="Toggle user, role or all mentions.")
@app_commands.describe(groups="The groups to be removed.")
async def remove_all(interaction: discord.Interaction, groups: typing.Literal["all", "roles", "users"]) -> None:
    temp_mention_list = read_file_content(
        "mention-remove-list", {interaction.guild_id: default_settings["mention-remove-list"]})
    temp_mention_list[interaction.guild_id].remove(
        groups) if groups in temp_mention_list[interaction.guild_id] else temp_mention_list[interaction.guild_id].add(groups)
    await write_file_content("mention-remove-list", temp_mention_list)
    await interaction.response.send_message(f"The group \"{groups}\" has been added. Note that this will take precedence over the remove list.")
    return


async def setup(bot):
    bot.tree.add_command(mention_command)

async def teardown(bot):
    bot.tree.remove_command("mention")