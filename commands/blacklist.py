import discord
from discord import app_commands
from index import read_file_content, write_file_content, default_settings
import typing

@app_commands.default_permissions(manage_guild=True)
@app_commands.checks.has_permissions(manage_guild=True)
@app_commands.command(name="blacklist", description="Blacklist users/roles for conversions.")
@app_commands.describe(action="The action to be performed.", user_object="The user you want to add or remove. Does nothing for other options.", role_object="The role you want to add or remove. Does nothing for other options.")
@app_commands.rename(user_object="user", role_object="role")
async def blacklist(interaction: discord.Interaction, action: typing.Literal["add", "remove", "list", "clear"], user_object: typing.Optional[discord.User], role_object: typing.Optional[discord.Role]) -> None:
    temp_blacklist_list = read_file_content(
        "blacklist-list", {interaction.guild_id: default_settings["blacklist-list"]})
    if action == "add":
        if user_object is None and role_object is None:
            await interaction.response.send_message(f"Please select a user or role to add.")
            return
        elif user_object is not None and role_object is None:
            if user_object.id in temp_blacklist_list[interaction.guild_id]["users"]:
                await interaction.response.send_message(f"The user {user_object.mention} already exists in the blacklist.", allowed_mentions=discord.AllowedMentions.none())
                return
            temp_blacklist_list[interaction.guild_id]["users"].add(
                user_object.id)
            await write_file_content("blacklist-list", temp_blacklist_list)
            await interaction.response.send_message(f"The user {user_object.mention} has been added to the blacklist.", allowed_mentions=discord.AllowedMentions.none())
            return
        elif user_object is None and role_object is not None:
            if role_object.id in temp_blacklist_list[interaction.guild_id]["roles"]:
                await interaction.response.send_message(f"The role {role_object.mention} already exists in the blacklist.", allowed_mentions=discord.AllowedMentions.none())
                return
            temp_blacklist_list[interaction.guild_id]["roles"].add(
                role_object.id)
            await write_file_content("blacklist-list", temp_blacklist_list)
            await interaction.response.send_message(f"The role {role_object.mention} has been added to the blacklist.", allowed_mentions=discord.AllowedMentions.none())
            return
        else:
            if user_object.id in temp_blacklist_list[interaction.guild_id]["users"] or role_object.id in temp_blacklist_list[interaction.guild_id]["roles"]:
                await interaction.response.send_message(f"The {'user '+user_object.mention+' and role '+role_object.mention if user_object.id in temp_blacklist_list[interaction.guild_id]['users'] and role_object.id in temp_blacklist_list[interaction.guild_id]['roles'] else 'user '+user_object.mention if user_object.id in temp_blacklist_list[interaction.guild_id]['users'] else 'role '+role_object.mention} already exists in the blacklist.", allowed_mentions=discord.AllowedMentions.none())
                return
            temp_blacklist_list[interaction.guild_id]["users"].add(
                user_object.id)
            temp_blacklist_list[interaction.guild_id]["roles"].add(
                role_object.id)
            await write_file_content("blacklist-list", temp_blacklist_list)
            await interaction.response.send_message(f"The {'user '+user_object.mention+' and role '+role_object.mention if user_object is not None and role_object is not None else 'user '+user_object.mention if user_object is not None else 'role '+role_object.mention} has been added to the blacklist.", allowed_mentions=discord.AllowedMentions.none())
            return
    elif action == "remove":
        if user_object is None and role_object is None:
            await interaction.response.send_message(f"Please select a user or role to remove.")
            return
        elif user_object is not None and role_object is None:
            if user_object.id in temp_blacklist_list[interaction.guild_id]["users"]:
                temp_blacklist_list[interaction.guild_id]["users"].remove(
                    user_object.id)
                await write_file_content("blacklist-list", temp_blacklist_list)
                await interaction.response.send_message(f"The user {user_object.mention} has been removed from the blacklist.", allowed_mentions=discord.AllowedMentions.none())
                return
            await interaction.response.send_message(f"The user {user_object.mention} does not exist in the blacklist. Please use the add option to add it.", allowed_mentions=discord.AllowedMentions.none())
            return
        elif user_object is None and role_object is not None:
            if role_object.id in temp_blacklist_list[interaction.guild_id]["roles"]:
                temp_blacklist_list[interaction.guild_id]["roles"].remove(
                    role_object.id)
                await write_file_content("blacklist-list", temp_blacklist_list)
                await interaction.response.send_message(f"The role {role_object.mention} has been removed from the blacklist.", allowed_mentions=discord.AllowedMentions.none())
                return
            await interaction.response.send_message(f"The role {role_object.mention} does not exist in the blacklist. Please use the add option to add it.", allowed_mentions=discord.AllowedMentions.none())
            return
        else:
            if user_object.id not in temp_blacklist_list[interaction.guild_id]["users"] or role_object.id not in temp_blacklist_list[interaction.guild_id]["roles"]:
                await interaction.response.send_message(f"The {'user '+user_object.mention+' and role '+role_object.mention if user_object.id not in temp_blacklist_list[interaction.guild_id]['users'] and role_object.id not in temp_blacklist_list[interaction.guild_id]['roles'] else 'user '+user_object.mention if user_object.id not in temp_blacklist_list[interaction.guild_id]['users'] else 'role '+role_object.mention} does not exist in the blacklist. Please use the add option to add it.", allowed_mentions=discord.AllowedMentions.none())
                return
            temp_blacklist_list[interaction.guild_id]["users"].remove(
                user_object.id)
            temp_blacklist_list[interaction.guild_id]["roles"].remove(
                role_object.id)
            await write_file_content("blacklist-list", temp_blacklist_list)
            await interaction.response.send_message(f"The {'user '+user_object.mention+' and role '+role_object.mention if user_object is not None and role_object is not None else 'user '+user_object.mention if user_object is not None else 'role '+role_object.mention} has been removed from the blacklist.", allowed_mentions=discord.AllowedMentions.none())
            return
    elif action == "list":
        if len(temp_blacklist_list[interaction.guild_id]['users']) == 0 and len(temp_blacklist_list[interaction.guild_id]['roles']) == 0:
            await interaction.response.send_message(f"There are no users/roles blacklisted for this server. Use the add option to add some.")
            return
        formatted_users = "\n".join(
            [f"- <@{item}>" for item in temp_blacklist_list[interaction.guild_id]["users"]])
        formatted_roles = "\n".join(
            [f"- <@&{item}>" for item in temp_blacklist_list[interaction.guild_id]["roles"]])
        await interaction.response.send_message((f"The users blacklisted are:\n{formatted_users}" if len(formatted_users) > 0 else "") + ("\n" if len(formatted_users) > 0 and len(formatted_roles) > 0 else "") + (f"The roles blacklisted are:\n{formatted_roles}" if len(formatted_roles) > 0 else ""), allowed_mentions=discord.AllowedMentions.none())
        return
    elif action == "clear":
        if len(temp_blacklist_list[interaction.guild_id]['users']) == 0 and len(temp_blacklist_list[interaction.guild_id]['roles']) == 0:
            await interaction.response.send_message(f"The blacklist is already empty. Please use the add option to add mentions.")
            return
        temp_blacklist_list[interaction.guild_id]["users"].clear()
        temp_blacklist_list[interaction.guild_id]["roles"].clear()
        await write_file_content("blacklist-list", temp_blacklist_list)
        await interaction.response.send_message(f"All users/roles have been removed from the blacklist.")
        return
    return


async def setup(bot):
    bot.tree.add_command(blacklist)


async def teardown(bot):
    bot.tree.remove_command("blacklist")
