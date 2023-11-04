import discord
from discord import app_commands
from index import read_file_content, write_file_content, group_template, default_settings
import re

# Regular expression pattern to match "domain.top-level-domain" format
domain_pattern = r"^[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"

conversion_command = group_template(
    name="conversion-list", description="Perform actions on the conversion list of domains.")

@app_commands.checks.has_permissions(manage_guild=True)
@conversion_command.command(description="Add a domain to convert")
@app_commands.describe(original="The domain to convert", converted="The new domain")
async def add(interaction: discord.Interaction, original: str, converted: str) -> None:
    
    # Check if the original domain matches the expected format
    if not re.match(domain_pattern, original) or not re.match(domain_pattern,converted):
        await interaction.response.send_message("Please provide the domains in the 'domain.top-level-domain' format.")
        return

    temp_conversion_list = read_file_content(
        "conversion-list", {interaction.guild_id: default_settings["conversion-list"]})
    if original in temp_conversion_list[interaction.guild_id]:
        await interaction.response.send_message(f"The domain {original} already exists in conversion list. Please use the update subcommand to update it or the remove subcommand to remove it.")
        return
    temp_conversion_list[interaction.guild_id][original] = converted
    await write_file_content("conversion-list", temp_conversion_list)
    await interaction.response.send_message(f"Added {converted} to list of conversions")
    return


async def update_autocomplete(interaction: discord.Interaction, current: str,) -> list[app_commands.Choice[str]]:
    conversion_dict = read_file_content(
        "conversion-list", {interaction.guild_id: default_settings["conversion-list"]})[interaction.guild_id]
    choices = [
        app_commands.Choice(name=original, value=original)
        for original, converted in conversion_dict.items()
        if current.lower() in original.lower()
    ]

    return choices[:25]

@app_commands.checks.has_permissions(manage_guild=True)
@conversion_command.command(description="Update a domain.")
@app_commands.describe(original="The original domain", updated="The updated domain")
@app_commands.autocomplete(original=update_autocomplete)
async def update(interaction: discord.Interaction, original: str, updated: str) -> None:

    # Check if the original domain matches the expected format
    if not re.match(domain_pattern, original) or not re.match(domain_pattern,updated):
        await interaction.response.send_message("Please provide the domains in the 'domain.top-level-domain' format.")
        return
    
    temp_conversion_list = read_file_content(
        "conversion-list", {interaction.guild_id: default_settings["conversion-list"]})
    if original in temp_conversion_list[interaction.guild_id]:
        temp_conversion_list[interaction.guild_id][original] = updated
        await write_file_content("conversion-list", temp_conversion_list)
        await interaction.response.send_message(f"The conversion for {original} was updated to {updated}.")
        return
    await interaction.response.send_message(f"The domain {original} does not exist in the conversion list. Please use the add subcommand to add it.")
    return


async def remove_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    conversion_dict = read_file_content(
        "conversion-list", {interaction.guild_id: default_settings["conversion-list"]})[interaction.guild_id]

    # Create a list of app_commands.Choice instances with "original : converted" format
    choices = [
        app_commands.Choice(name=f"{original} : {converted}", value=original)
        for original, converted in conversion_dict.items()
        if current.lower() in original.lower()
    ]

    return choices[:25]

@app_commands.checks.has_permissions(manage_guild=True)
@conversion_command.command(description="Remove a domain to convert")
@app_commands.describe(original="The domain to remove")
@app_commands.autocomplete(original=remove_autocomplete)
async def remove(interaction: discord.Interaction, original: str) -> None:

    # Check if the original domain matches the expected format
    if not re.match(domain_pattern, original):
        await interaction.response.send_message("Please provide the domains in the 'domain.top-level-domain' format.")
        return
    
    temp_conversion_list = read_file_content(
        "conversion-list", {interaction.guild_id: default_settings["conversion-list"]})
    if original in temp_conversion_list[interaction.guild_id]:
        del temp_conversion_list[interaction.guild_id][original]
        await write_file_content("conversion-list", temp_conversion_list)
        await interaction.response.send_message(f"Removed {original} from the list of conversions")
        return
    await interaction.response.send_message(f"The domain {original} does not exist in conversion list. Please use the add subcommand to add it.")
    return

@app_commands.checks.has_permissions(manage_guild=True)
@conversion_command.command(description="List all domains to convert")
async def list(interaction: discord.Interaction) -> None:
    temp_conversion_list = read_file_content(
        "conversion-list", {interaction.guild_id: default_settings["conversion-list"]})
    # Create a formatted string with bullet points
    formatted_list = "\n".join(
        [f"- {key} : {value}" for key, value in temp_conversion_list[interaction.guild_id].items()])

    await interaction.response.send_message(f"Domains to convert:\n{formatted_list}")
    return


async def setup(bot):
    bot.tree.add_command(conversion_command)

async def teardown(bot):
    bot.tree.remove_command("conversion-list")