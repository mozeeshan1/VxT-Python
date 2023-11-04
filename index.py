import json
import discord
import os
import asyncio
from discord import app_commands
from discord.ext import commands
import datetime
import traceback
import requests
import sys


import re
from collections import defaultdict


default_settings = {"conversion-list": {"twitter.com": "fxtwitter.com",
                                        "instagram.com": "ddinstagram.com", "tiktok.com": "tiktxk.com"}, "name-preference-list": "display name", "mention-remove-list": [], "toggle-list": {"all": True, "text": True, "images": True, "videos": True, "polls": True}, "quote-tweet-list": {"link_conversion": {"follow tweets": True, "all": True, "text": True, "images": True, "videos": True, "polls": True}, "remove quoted tweet": False}, "message-list": {"delete_original": True, "other_webhooks": False}, "retweet-list": {"delete_original_tweet": False}, "direct-media-list": {"toggle": {"images": False, "videos": False}, "channel": ["allow"], "multiple_images": {"convert": True, "replace_with_mosaic": True}, "quote_tweet": {"convert": False, "prefer_quoted_tweet": True}}, "translate-list": {"toggle": False, "language": "en"}, "delete-bot-message-list": {"toggle": True, "number": 1}, "webhook-list": {"preference": "webhooks", "reply": False}, "blacklist-list": {"users": [], "roles": []}}

master_settings = {}


class custom_app_command_error(discord.app_commands.AppCommandError):
    def __init__(self, custom_message: str, *args: object) -> None:
        super().__init__(*args)
        self.custom_message = custom_message


class group_template(app_commands.Group):
    ...


async def check_if_bot_owner(interaction: discord.Interaction) -> bool:
    if interaction.user.id == 231026645224390656:
        return True
    raise custom_app_command_error(
        "Only the bot owner can use these commands.")


async def command_error_handler(error_interaction, error=None):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get the traceback of the error
    error_traceback = traceback.format_exc()

    # Log to console
    print(f"App command error at {current_time}:")
    print(error_interaction.command)
    print(error_interaction.data)
    print(error)
    print(error_traceback)
    # Log to file
    with open("error_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"\nApp command error at {current_time}:\n")
        log_file.write(str(error_interaction.command) + "\n")
        log_file.write(str(error_interaction.data) + "\n")
        log_file.write(str(error) + "\n")
        log_file.write(error_traceback + "\n")

    temp_error_list = read_file_content("error-list")
    if (str(error) in temp_error_list):
        await error_interaction.response.send_message(temp_error_list[str(error)])
        return
    elif (hasattr(error, "custom_message")):
        print("CUSTOM MESSAGE:", error.custom_message)
        with open("error_log.txt", "a") as log_file:
            log_file.write("Custom Message: " + error.custom_message + "\n")
        await error_interaction.response.send_message(error.custom_message)
        return
    elif (hasattr(error, "missing_permissions")):
        await error_interaction.response.send_message(str(error))
        return
    await error_interaction.response.send_message(f"Error encountered. To resolve the issue, please ask the developer to check the error at timestamp: {current_time}")
    return


async def on_bot_error(error_event, *args, **kwargs):

    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Convert args and kwargs to string representations
    args_str = ', '.join(map(str, args))
    kwargs_str = ', '.join(f"{k}={v}" for k, v in kwargs.items())

    # Get the exception information
    exc_type, exc_value, exc_traceback = sys.exc_info()

    # Initialize channel to None
    channel = None

    # Extract the message object from args if it's a Message event
    message = next(
        (arg for arg in args if isinstance(arg, discord.Message)), None)
    if message:
        channel = message.channel

    # If it's a RawReactionActionEvent, extract the channel_id and get the channel
    if not channel:
        raw_event = next((arg for arg in args if isinstance(
            arg, discord.RawReactionActionEvent)), None)
        if raw_event:
            channel = await bot.fetch_channel(raw_event.channel_id)

    if exc_type == discord.errors.Forbidden and exc_value.code == 50013:
        if channel:
            # Inspect the traceback to check if the error is related to webhooks or message deletion
            tb_str = "".join(traceback.format_tb(exc_traceback))
            if 'webhooks' in tb_str:
                permission_needed = "'Manage Webhooks'"
            elif 'delete_message' in tb_str:
                permission_needed = "'Manage Messages'"
            elif 'add_reaction' in tb_str:
                permission_needed = "'Add Reactions'"
            else:
                permission_needed = "the required"

            # Send a message to the channel about the missing permissions
            await channel.send(f"I'm missing {permission_needed} permissions needed to perform this action.")

    # Get the traceback of the error
    error_traceback = traceback.format_exc()

    print(
        f"Bot Error at:{current_time}\n{error_event}\nArgs: {args_str}\nKwargs: {kwargs_str}\n{error_traceback}")

    with open("error_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"\nBot Error at {current_time}:\n")
        log_file.write(str(error_event) + "\n")
        log_file.write(f"Args: {args_str}\n")
        log_file.write(f"Kwargs: {kwargs_str}\n")
        log_file.write(error_traceback + "\n")


async def on_bot_command_error(context, error):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get the traceback of the error
    error_traceback = traceback.format_exc()

    print(
        f"Bot Command Error at:{current_time}\nContext: {context}\nError: {error}\n{error_traceback}")

    with open("error_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"\nBot command Error at {current_time}:\n")
        log_file.write(f"Context: {context}\n")
        log_file.write(f"Error: {error}\n")
        log_file.write(error_traceback+"\n")


def convert_str_to_int(data):
    if isinstance(data, dict):
        # Recursively convert dictionary contents
        return {int(k) if isinstance(k, str) and k.isdigit() else k: convert_str_to_int(v) for k, v in data.items()}
    elif isinstance(data, list):
        # Convert the top-level list to a set, and any nested lists to tuples
        return set(convert_str_to_int(item) if not isinstance(item, list) else tuple(item) for item in data)
    elif isinstance(data, str) and data.isdigit():
        # Convert numeric strings to integers
        return int(data)
    else:
        # Return all other data types unchanged
        return data


def convert_set_to_list(data):
    if isinstance(data, dict):
        return {k: convert_set_to_list(v) for k, v in data.items()}
    elif isinstance(data, set):
        return list(data)
    else:
        return data


def read_file_content(file_name, empty_value={}):
    # file_path = os.path.join(os.getcwd(), "lists", file_name)
    file_path = os.path.join(os.getcwd(
    ), file_name) if file_name == "error-list" else os.path.join(os.getcwd(), "lists", file_name)

    # Create the "lists" folder if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Check if the file exists
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            content = json.load(file)
            return convert_str_to_int(content)
    else:
        # Create the file if it doesn't exist
        with open(file_path, 'w') as file:
            json.dump(empty_value, file)
        return empty_value


async def write_file_content(file_name, modified_content):
    file_path = os.path.join(os.getcwd(), "lists", file_name)
    file_path = os.path.join(os.getcwd(
    ), file_name) if file_name == "error-list" else os.path.join(os.getcwd(), "lists", file_name)

    # Convert sets to lists before writing to file
    modified_content = convert_set_to_list(modified_content)

    # Create the "lists" folder if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w') as file:
        json.dump(modified_content, file)
        return True


async def load_settings():
    # Path to the commands directory
    lists_dir = "lists"

    # List all files in the commands directory
    for filename in os.listdir(lists_dir):

        temp_file = read_file_content(filename, default_settings[filename])
        # Update the master_settings with the data from the file
        for guild_id, settings in temp_file.items():
            if guild_id not in master_settings:
                master_settings[guild_id] = {}
            master_settings[guild_id][filename[:-5]] = settings

    return True


async def load_all_extensions(bot):
    # Path to the commands directory
    commands_dir = "commands"

    # List all files in the commands directory
    for filename in os.listdir(commands_dir):
        # Check if the file is a Python file
        if filename.endswith(".py"):
            # Construct the module path
            extension_name = f"{commands_dir}.{filename[:-3]}"
            print(extension_name)
            # Load the extension
            await bot.load_extension(extension_name, package=None)
    return True


async def reload_all_extensions(bot=None, client=None):
    temp_extensions = list(bot.extensions.keys())
    # List all extension names in bot
    for index, extension_name in enumerate(temp_extensions, start=1):
        if extension_name == "commands.command-sync":
            continue
        print(f"{index}. {extension_name}")
        # Reload the extension
        await bot.reload_extension(extension_name, package=None)
    return True


def convert_to_fxtwitter_domain(processed_message, message, guild_id, domain_urls, link_responses):
    if master_settings[guild_id]["toggle"] != default_settings["toggle-list"] or master_settings[guild_id]["retweet"] != default_settings["retweet-list"] or master_settings[guild_id]["quote-tweet"] != default_settings["quote-tweet-list"] or master_settings[guild_id]["direct-media"] != default_settings["direct-media-list"]:
        # Regular expression to extract the status number from the Twitter link
        pattern = r"/status/(\d+)"
        temp_new_domain_urls = domain_urls
        direct_media_urls = set()
        mosaic_direct_media_urls = set()
        for link in domain_urls:
            match = re.search(pattern, link)
            if match:
                status_number = match.group(1)

                # Construct the API URL
                api_url = f"https://api.fxtwitter.com/i/status/{status_number}"

                # Send a request to the API URL (you can customize this part as needed)
                response = requests.get(api_url)

                # Check the response (for demonstration purposes, we'll just print it)
                if response.status_code == 200:
                    link_responses[link] = response.json()["tweet"]
                else:
                    print(
                        f"Failed to retrieve data for status {status_number}. HTTP Status Code: {response.status_code}")

            if master_settings[guild_id]["toggle"] != default_settings["toggle-list"]:
                if not master_settings[guild_id]["toggle"]["all"] or (not master_settings[guild_id]["toggle"]["polls"] and (("quote" in link_responses[link] and "polls" in link_responses[link]["quote"]) or ("polls" in link_responses[link]))) or (not master_settings[guild_id]["toggle"]["videos"] and (("quote" in link_responses[link] and "media" in link_responses[link]["quote"] and "videos" in link_responses[link]["quote"]["media"]) or ("media" in link_responses[link] and "videos" in link_responses[link]["media"]))) or (not master_settings[guild_id]["toggle"]["images"] and (("quote" in link_responses[link] and "media" in link_responses[link]["quote"] and "photos" in link_responses[link]["quote"]["media"]) or ("media" in link_responses[link] and "photos" in link_responses[link]["media"]))):
                    temp_new_domain_urls.discard(link)
                else:
                    temp_new_domain_urls.add(link)

            if not master_settings[guild_id]["quote-tweet"]["link_conversion"]["follow tweets"]:
                if (not master_settings[guild_id]["quote-tweet"]["link_conversion"]["all"] or (not master_settings[guild_id]["quote-tweet"]["link_conversion"]["polls"] and (("quote" in link_responses[link] and "polls" in link_responses[link]["quote"]) or "polls" in link_responses[link])) or (not master_settings[guild_id]["quote-tweet"]["link_conversion"]["videos"] and (("quote" in link_responses[link] and "media" in link_responses[link]["quote"] and "videos" in link_responses[link]["quote"]["media"]) or ("media" in link_responses[link] and "videos" in link_responses[link]["media"]))) or (not master_settings[guild_id]["quote-tweet"]["link_conversion"]["images"] and (("quote" in link_responses[link] and "media" in link_responses[link]["quote"] and "photos" in link_responses[link]["quote"]["media"]) or ("media" in link_responses[link] and "photos" in link_responses[link]["media"])))):
                    temp_new_domain_urls.discard(link)
                else:
                    temp_new_domain_urls.add(link)

            if master_settings[guild_id]["direct-media"]["toggle"] != default_settings["direct-media-list"]["toggle"] and ("allow" in master_settings[guild_id]["direct-media"]["channel"] or ("allow", message.channel.mention) in master_settings[guild_id]["direct-media"]["channel"]):
                if (master_settings[guild_id]["direct-media"]["toggle"]["images"] and "media" in link_responses[link] and "photos" in link_responses[link]["media"]) or (master_settings[guild_id]["direct-media"]["toggle"]["videos"] and "media" in link_responses[link] and "videos" in link_responses[link]["media"]):
                    direct_media_urls.add(link)

                if not master_settings[guild_id]["direct-media"]["multiple_images"]["convert"] and (("media" in link_responses[link] and "mosaic" in link_responses[link]["media"]) or "quote" in link_responses[link] and "media" in link_responses[link]["quote"] and "mosaic" in link_responses[link]["quote"]["media"]):
                    direct_media_urls.discard(link)

                if master_settings[guild_id]["direct-media"]["multiple_images"]["convert"] and master_settings[guild_id]["direct-media"]["multiple_images"]["replace_with_mosaic"] and (("media" in link_responses[link] and "mosaic" in link_responses[link]["media"]) or "quote" in link_responses[link] and "media" in link_responses[link]["quote"] and "mosaic" in link_responses[link]["quote"]["media"]):
                    direct_media_urls.discard(link)
                    mosaic_direct_media_urls.add(link)

                if master_settings[guild_id]["direct-media"]["quote_tweet"]["convert"] and ((master_settings[guild_id]["direct-media"]["toggle"]["images"] and "quote" in link_responses[link] and "media" in link_responses[link]["quote"] and "images" in link_responses[link]["quote"]["media"]) or (master_settings[guild_id]["direct-media"]["toggle"]["videos"] and "quote" in link_responses[link] and "media" in link_responses[link]["quote"] and "videos" in link_responses[link]["quote"]["media"])):
                    direct_media_urls.add(link)

                if master_settings[guild_id]["direct-media"]["quote_tweet"]["convert"] and master_settings[guild_id]["direct-media"]["multiple_images"]["convert"] and (master_settings[guild_id]["direct-media"]["toggle"]["images"] and "quote" in link_responses[link] and "media" in link_responses[link]["quote"] and "mosaic" in link_responses[link]["quote"]["media"]) and master_settings[guild_id]["direct-media"]["multiple_images"]["replace_with_mosaic"]:
                    mosaic_direct_media_urls.add(link)

        # Regular expression to match any fxtwitter.com URLs and extract the entire URL including query parameters
        pattern = r"(https?://(?:\w+\.)?fxtwitter\.com/(?:\w+/)?status/(\d+)(?:\?\S*)?)"

        # Find all matches of fxtwitter.com URLs in the message
        fxtwitter_matches = re.findall(pattern, processed_message)

        # Iterate over the matches to make API requests
        for full_url, status_number in fxtwitter_matches:

            # Construct the API URL
            api_url = f"https://api.fxtwitter.com/i/status/{status_number}"

            # Send a request to the API URL
            response = requests.get(api_url)

            # Check the response and store it if successful
            if response.status_code == 200:
                link_responses[full_url] = response.json()["tweet"]
            else:
                print(
                    f"Failed to retrieve data for fxtwitter status {status_number}. HTTP Status Code: {response.status_code}")

        urls_to_delete = set()
        if master_settings[guild_id]["retweet"]["delete_original_tweet"]:
            # Create a dictionary to map the text to the original tweet URL
            original_tweet_text_to_url = {}

            # First, populate the dictionary with original tweet texts and their URLs
            for url, response in link_responses.items():
                if "RT @" not in response["text"]:
                    original_tweet_text_to_url[response["text"]] = url

            # Now, iterate over the API responses to find retweets
            for url, response in link_responses.items():
                tweet_text = response["text"]
                # Check if the response text indicates a retweet
                if tweet_text.startswith("RT @"):
                    # Extract the original tweet text from the retweet text
                    original_text = tweet_text[tweet_text.index(":") + 2:]
                    # Remove trailing ellipsis (both types) if present
                    original_text = original_text.replace(
                        "...", "").replace("…", "").strip()

                    # Check if the original tweet text is present in any of the keys of our dictionary
                    for original_tweet_text in original_tweet_text_to_url.keys():
                        # Check if the original tweet text starts with the truncated retweet text
                        if original_tweet_text.startswith(original_text):
                            # If so, add the original tweet URL to the set of URLs to remove
                            urls_to_delete.add(
                                original_tweet_text_to_url[original_tweet_text])
                            break  # No need to check further once a match is found

        if master_settings[guild_id]["quote-tweet"]["remove quoted tweet"]:
            # Create a dictionary to map the original tweet ID to the quote tweet URL
            original_tweet_id_to_quote_tweet_url = {}

            # First, populate the dictionary with original tweet IDs and their corresponding quote tweet URLs
            for url, response in link_responses.items():
                if "quote" in response:
                    original_tweet_id = response["quote"]["id"]
                    original_tweet_id_to_quote_tweet_url[original_tweet_id] = url

            # Now, iterate over the set of URLs to find original tweets
            for url, response in link_responses.items():
                tweet_id = response["id"]
                if tweet_id in original_tweet_id_to_quote_tweet_url:
                    # If the original tweet's ID is in our dictionary, add the url to our URLs to remove
                    urls_to_delete.add(url)

        # Remove URLs
        for url in urls_to_delete:
            processed_message = processed_message.replace(url, '')

        for url in mosaic_direct_media_urls:
            new_url = ""
            if master_settings[guild_id]["direct-media"]["quote_tweet"]["prefer_quoted_tweet"] and "quote" in link_responses[url]:
                new_url = link_responses[url].get("quote", {}).get("media", {}).get(
                    'mosaic', {}).get("formats", {}).get("jpeg", "")
            else:
                new_url = link_responses[url].get("media", {}).get(
                    'mosaic', {}).get("formats", {}).get("jpeg", "")
            processed_message = processed_message.replace(url, new_url)

        for url in direct_media_urls:
            new_url = ""
            if master_settings[guild_id]["direct-media"]["multiple_images"]["convert"] and master_settings[guild_id]["direct-media"]["multiple_images"]["replace_with_mosaic"] and master_settings[guild_id]["direct-media"]["quote_tweet"]["prefer_quoted_tweet"] and "quote" in link_responses[url] and "media" in link_responses[url]["quote"] and "mosaic" in link_responses[url]["quote"]["media"]:
                new_url = link_responses[url].get("quote", {}).get("media", {}).get(
                    'mosaic', {}).get("formats", {}).get("jpeg", "")
            elif master_settings[guild_id]["direct-media"]["multiple_images"]["convert"] and master_settings[guild_id]["direct-media"]["quote_tweet"]["prefer_quoted_tweet"] and "quote" in link_responses[url] and "media" in link_responses[url]["quote"] and "mosaic" in link_responses[url]["quote"]["media"]:
                new_url = f"https://d.fxtwitter.com/i/status/{link_responses[url]['quote']['id']}/"
            elif master_settings[guild_id]["direct-media"]["quote_tweet"]["prefer_quoted_tweet"] and "quote" in link_responses[url]:
                new_url = f"https://d.fxtwitter.com/i/status/{link_responses[url]['quote']['id']}/"
            else:
                new_url = f"https://d.fxtwitter.com/i/status/{link_responses[url]['id']}/"
            processed_message = processed_message.replace(url, new_url)

        for url in temp_new_domain_urls:
            new_url = ""
            if master_settings[guild_id]["translate"]["toggle"]:
                new_url = f"https://fxtwitter.com/i/status/{link_responses[url]['id']}/{master_settings[guild_id]['translate']['language']}"
            else:
                new_url = f"https://fxtwitter.com/i/status/{link_responses[url]['id']}/"
            processed_message = processed_message.replace(url, new_url)

        return processed_message

    if master_settings[guild_id]["translate"]["toggle"]:
        pattern = r"/status/(\d+)"
        for link in domain_urls:
            match = re.search(pattern, link)
            if match:
                status_number = match.group(1)
            converted_url = f"https://fxtwitter.com/i/status/{status_number}/{master_settings[guild_id]['translate']['language']}"
            processed_message = processed_message.replace(link, converted_url)
        return processed_message
    return processed_message


def convert_domains_in_message(message, guild_id, urls):
    processed_message = message.content
    # Group URLs by their domain
    domain_groups = defaultdict(list)
    for url in urls:
        # Extract the domain including subdomains
        full_domain = re.search(r'https?://([\w.-]+)/?', url).group(1)
        # Extract the main domain (without subdomains)
        domain_parts = full_domain.split('.')
        # e.g., "instagram.com" from "www.instagram.com"
        main_domain = '.'.join(domain_parts[-2:])

        if url not in domain_groups[main_domain]:
            domain_groups[main_domain].append(url)

    # Process each domain group
    for domain, domain_urls in domain_groups.items():
        domain_urls = set(domain_urls)
        if domain in master_settings[guild_id]["conversion"]:
            # Here, we can add preprocessing checks based on the domain and guild settings
            # For example, for twitter, check if any URL in domain_urls is a retweet with photos, etc.

            link_responses = {}

            if (domain == "twitter.com" or domain == "x.com") and master_settings[guild_id]["conversion"][domain] == "fxtwitter.com":
                processed_message = convert_to_fxtwitter_domain(
                    processed_message, message, guild_id, domain_urls, link_responses)
                continue

            # Replace all URLs of that domain with the desired domain
            for url in domain_urls:
                converted_url = url.replace(
                    domain, master_settings[guild_id]["conversion"][domain])
                processed_message = processed_message.replace(
                    url, converted_url)

    return processed_message


config = open("config.json")
config = json.load(config)


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(".", intents=intents)


@bot.event
async def on_ready():
    print("Starting bot")
    await bot.wait_until_ready()
    print("Bot is ready")
    await bot.tree.sync()
    for guild in bot.guilds:
        for filename in default_settings.keys():
            temp_list = read_file_content(
                filename, {guild.id: default_settings[filename]})
            if guild.id not in temp_list:
                temp_list[guild.id] = default_settings[filename]
            await write_file_content(filename, temp_list)
    await load_settings()
    await bot.change_presence(activity=discord.Game(name=f"in {len(bot.guilds)} servers"))
    print(f'We have logged in as {bot.user}')
    print(f"{len(await bot.tree.fetch_commands())} application commands loaded")


@bot.event
async def on_guild_join(guild):
    for filename in default_settings.keys():
        temp_list = read_file_content(
            filename, {guild.id: default_settings[filename]})
        temp_list[guild.id] = default_settings[filename]
        await write_file_content(filename, temp_list)
    await load_settings()
    await bot.change_presence(activity=discord.Game(name=f"in {len(bot.guilds)} servers"))


@bot.event
async def on_guild_remove(guild):
    await bot.change_presence(activity=discord.Game(name=f"in {len(bot.guilds)} servers"))


@bot.event
async def on_app_command_completion(interaction, command):
    await load_settings()


@bot.event
async def on_raw_reaction_add(payload):
    if master_settings == {}:
        return
    if not master_settings[payload.guild_id]["delete-bot-message"]["toggle"]:
        return
    channel = await bot.fetch_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    if message.webhook_id:
        temp_webhook = await bot.fetch_webhook(message.webhook_id)
        temp_bot = await message.guild.fetch_member(temp_webhook.user.id)
        if temp_bot.id == bot.user.id:
            reaction = next(
                (react for react in message.reactions if "❌" in react.emoji), None)
            if reaction is None:
                return
            if reaction.count > master_settings[payload.guild_id]["delete-bot-message"]["number"]:
                await message.delete()
                return
    if message.author == bot.user:
        reaction = next(
            (react for react in message.reactions if "❌" in react.emoji), None)
        if reaction.count > master_settings[payload.guild_id]["delete-bot-message"]["number"]:
            await message.delete()
            return


@bot.event
async def on_message(message):
    if master_settings == {}:
        return
    if message.author == bot.user:
        return

    if not master_settings[message.guild.id]["message"]["other_webhooks"] and message.webhook_id:
        return

    if message.webhook_id:
        temp_webhook = await bot.fetch_webhook(message.webhook_id)
        temp_bot = await message.guild.fetch_member(temp_webhook.user.id)
        if temp_bot.id in master_settings[message.guild.id]["blacklist"]["users"] or any(role.id in master_settings[message.guild.id]["blacklist"]["roles"] for role in temp_bot.roles):
            return

    if not message.webhook_id and (message.author.id in master_settings[message.guild.id]["blacklist"]["users"] or any(role.id in master_settings[message.guild.id]["blacklist"]["roles"] for role in message.author.roles)):
        return

    # if message.content.startswith('$hello'):
    #     await message.channel.send('Hello!')
    #     print("said hello", message.author.display_name,
    #           message.author.display_avatar)

    # Extract all URLs from the message
    urls = re.findall(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content)

    # Check if the conversion list has any domains and if the message has any URLs
    if len(master_settings[message.guild.id]["conversion"].keys()) > 0 and urls:
        converted_domains_message = convert_domains_in_message(
            message, message.guild.id, urls)
        if converted_domains_message == message.content:
            return
        msg_mentions = discord.AllowedMentions.all()
        msg_send_mentions = discord.AllowedMentions.all()
        if len(master_settings[message.guild.id]["mention-remove"]) > 0 and (len(message.mentions) > 0 or len(message.role_mentions) > 0):
            users_mentioned = message.mentions
            roles_mentioned = message.role_mentions
            # Filter out members and roles whose mention is in the mention_set
            filtered_members = [
                user.id for user in users_mentioned if user.mention not in master_settings[message.guild.id]["mention-remove"]]
            filtered_roles = [
                role.id for role in roles_mentioned if role.mention not in master_settings[message.guild.id]["mention-remove"]]
            msg_mentions = discord.AllowedMentions(
                everyone="everyone" not in master_settings[message.guild.id]["mention-remove"], users=filtered_members, roles=filtered_roles)
            filtered_send_members = [
                user for user in users_mentioned if user.mention not in master_settings[message.guild.id]["mention-remove"]]
            filtered_send_roles = [
                role for role in roles_mentioned if role.mention not in master_settings[message.guild.id]["mention-remove"]]
            msg_send_mentions = discord.AllowedMentions(
                everyone="everyone" not in master_settings[message.guild.id]["mention-remove"], users=filtered_send_members, roles=filtered_send_roles)

        sent_message = None
        if master_settings[message.guild.id]["webhook"]["preference"] == "webhooks":

            channel_webhooks = None
            if "thread" in message.channel.type:
                channel_webhooks = await message.channel.parent.webhooks()
            else:
                channel_webhooks = await message.channel.webhooks()
            matching_webhook = next(
                (webhook for webhook in channel_webhooks if bot.user.id == webhook.user.id), None)

            if not matching_webhook:
                if "thread" in message.channel.type:
                    matching_webhook = await message.channel.parent.create_webhook(name="VxT", reason="To send messages with converted links.")
                else:
                    matching_webhook = await message.channel.create_webhook(name="VxT", reason="To send messages with converted links.")

            # Parameters to always include
            webhook_params = {
                'content': converted_domains_message,
                'wait': True,
                'username': message.author.display_name if master_settings[message.guild.id]["name-preference"] == "display name" else message.author.name,
                'avatar_url': message.author.display_avatar,
                'files': [await attachment.to_file() for attachment in message.attachments],
                'allowed_mentions': msg_mentions
            }

            # Conditionally add the 'thread' parameter if the channel type is a thread
            if "thread" in message.channel.type:
                webhook_params['thread'] = message.channel.id
            sent_message = await matching_webhook.send(**webhook_params)

        elif master_settings[message.guild.id]["webhook"]["preference"] == "bot" and master_settings[message.guild.id]["webhook"]["reply"]:
            sent_message = await message.reply(content=converted_domains_message, files=[await attachment.to_file() for attachment in message.attachments], allowed_mentions=msg_mentions)
        else:
            sent_message = await message.channel.send(content=converted_domains_message, files=[await attachment.to_file() for attachment in message.attachments], allowed_mentions=msg_send_mentions)

        if master_settings[message.guild.id]["delete-bot-message"]["toggle"]:
            await sent_message.add_reaction("❌")

        if master_settings[message.guild.id]["message"]["delete_original"] == True:
            await message.delete()


async def main():
    await load_all_extensions(bot)
    bot.tree.on_error = command_error_handler
    bot.on_error = on_bot_error
    bot.on_command_error = on_bot_command_error
    await bot.start(config["TOKEN"], reconnect=True)


# Use asyncio.run() only if this script is executed directly
if __name__ == "__main__":
    asyncio.run(main())
