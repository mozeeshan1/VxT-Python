import discord
from discord import app_commands
from index import read_file_content, write_file_content, group_template, check_if_bot_owner





error_command = group_template(
    name="error-list", description="Perform actions on the list of custom error responses.")



@app_commands.check(check_if_bot_owner)
@error_command.command(name="add", description="Add a custom response to the error.")
@app_commands.describe(error="The error message.", response="The response to the error message.")
async def add(interaction: discord.Interaction, error: str, response: str) -> None:
    temp_error_list = read_file_content("error-list")
    if error in temp_error_list:
        await interaction.response.send_message(f"The error: \n- {error}\nalready exists. Please use the update subcommand to update the response.")
        return
    temp_error_list[error] = response
    await write_file_content("error-list", temp_error_list)
    await interaction.response.send_message(f"The error:\n- {error}\nand its response:\n- {response}\nhave been added")
    return


async def error_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    temp_error_list = read_file_content("error-list")
    choices = [
        app_commands.Choice(name=error, value=error)
        for error, response in temp_error_list.items()
        if current.lower() in error.lower()
    ]
    return choices[:25]



@app_commands.check(check_if_bot_owner)
@error_command.command(name="update", description="Update the response to an error.")
@app_commands.describe(error="The error message to update.", response="The new response.")
@app_commands.autocomplete(error=error_autocomplete)
async def update(interaction: discord.Interaction, error: str, response: str) -> None:
    temp_error_list = read_file_content("error-list")
    if error in temp_error_list:
        temp_error_list[error] = response
        await write_file_content("error-list", temp_error_list)
        await interaction.response.send_message(f"The error:\n- {error}\nhas an updated response:\n- {response}")
        return
    await interaction.response.send_message(f"The error:\n- {error}\ndoes not exist in the list. Please use the add subcommand to add it.")
    return



@app_commands.check(check_if_bot_owner)
@error_command.command(name="remove", description="Remove an error from the list.")
@app_commands.describe(error="The error to remove.")
@app_commands.autocomplete(error=error_autocomplete)
async def remove(interaction: discord.Interaction, error: str) -> None:
    temp_error_list = read_file_content("error-list")
    if error in temp_error_list:
        del temp_error_list[error]
        await write_file_content("error-list",temp_error_list)
        await interaction.response.send_message(f"The error:\n- {error}\nand its response have been removed from the list.")
        return
    await interaction.response.send_message(f"The error:\n- {error}\ndoes not exist in the list. Please use the add subcommand to add it.")
    return



@app_commands.check(check_if_bot_owner)
@error_command.command(name="list", description="List all the errors and their responses.")
async def list(interaction: discord.Interaction) -> None:
    temp_error_list = read_file_content("error-list")
    # Create a formatted string with bullet points
    formatted_list = "\n".join(
        [f"- {key} ---- {value}" for key, value in temp_error_list.items()])
    await interaction.response.send_message(f"The errors and their responses:\n{formatted_list}")
    return


async def setup(bot):
    bot.tree.add_command(error_command)

async def teardown(bot):
    bot.tree.remove_command("error-list")