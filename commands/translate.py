import discord
from discord import app_commands
from index import read_file_content, write_file_content, default_settings, group_template
import langcodes
import pycountry


translate_command = group_template(
    name="translate", description="Change the translation behaviour of the conversions.")


@app_commands.checks.has_permissions(manage_guild=True)
@translate_command.command(name="toggle", description="Toggle the translation of tweets. Off by default.")
async def toggle(interaction: discord.Interaction) -> None:
    temp_translate_list = read_file_content(
        "translate-list", {interaction.guild_id: default_settings["translate-list"]})
    temp_translate_list[interaction.guild_id]["toggle"] = not temp_translate_list[interaction.guild_id]["toggle"]
    await write_file_content("translate-list", temp_translate_list)
    await interaction.response.send_message(f"Translation for converted tweets is {'on.' if temp_translate_list[interaction.guild_id]['toggle'] else 'off.'}")
    return


async def language_autocomplete(interaction:discord.Interaction,current:str)->list[app_commands.Choice[str]]:
    filtered_lang_names=[item.name for item in list(pycountry.languages) if hasattr(item,"alpha_2") if langcodes.Language.get(item.alpha_2).is_valid()]
    return [app_commands.Choice(name=lang,value=lang) for lang in filtered_lang_names if current.lower() in lang.lower()][:25]



@app_commands.checks.has_permissions(manage_guild=True)
@translate_command.command(name="language", description="Change the language the tweets are translated to. English by default.")
@app_commands.rename(t_lang="language")
@app_commands.describe(t_lang="The language to translate to. ISO 639 code or full name in English.")
@app_commands.autocomplete(t_lang=language_autocomplete)
async def language(interaction: discord.Interaction, t_lang: str) -> None:
    await interaction.response.defer()
    lang_codes={item.name:item.alpha_2 for item in list(pycountry.languages) if hasattr(item,"alpha_2") if langcodes.Language.get(item.alpha_2).is_valid()}
    if t_lang not in lang_codes.keys():
        await interaction.edit_original_response(content=f"Please select a language from the predefined options.")
        return
    temp_translate_list=read_file_content("translate-list",{interaction.guild_id:default_settings["translate-list"]})
    temp_translate_list[interaction.guild_id]["language"]=lang_codes[t_lang]
    await write_file_content("translate-list",temp_translate_list)
    await interaction.edit_original_response(content=f"Converted tweets will now be converted to {t_lang}.{' Translation for converted tweets is currently off. Please turn it on using the toggle subcommand for the translation to work.' if not temp_translate_list[interaction.guild_id]['toggle'] else ''}")
    return


async def setup(bot):
    bot.tree.add_command(translate_command)


async def teardown(bot):
    bot.tree.remove_command("translate")
