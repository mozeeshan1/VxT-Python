import os
import json



default_settings = {"conversion-list": {"twitter.com": "fxtwitter.com", "x.com": "fxtwitter.com",
                                        "instagram.com": "ddinstagram.com", "tiktok.com": "tiktxk.com"}, "name-preference-list": "display name", "mention-remove-list": [], "toggle-list": { "all":True,"text": True, "images": True, "videos": True, "polls": True}, "quote-tweet-list": {"link_conversion": {"follow tweets": True, "all": True, "text": True, "images": True, "videos": True, "polls": True}, "remove quoted tweet": False}, "message-list": {"delete_original": True, "other_webhooks": False}, "retweet-list": {"delete_original_tweet": False}, "direct-media-list": {"toggle": {"images": False, "videos": False}, "channel": ["allow"], "multiple_images": {"convert": True, "replace_with_mosaic": True}, "quote_tweet": {"convert": False, "prefer_quoted_tweet": True}}, "translate-list": {"toggle": False, "language": "en"}, "delete-bot-message-list": {"toggle": False, "number": 1}, "webhook-list": {"preference": "webhooks", "reply": False}, "blacklist-list": {"users": [], "roles": []}}

# Get the current working directory and join it with 'list'
list_folder = os.path.join(os.getcwd(), "lists")

# Dictionary to hold the count of differences for each file/list
differences_summary = {}

for list_key, default_value in default_settings.items():
    file_path = os.path.join(list_folder, list_key )
    try:
        with open(file_path, "r") as file:
            # Each file is expected to be a JSON object with id keys and setting values
            file_data = json.load(file)
    except FileNotFoundError:
        print(f"File '{file_path}' not found. Skipping.")
        continue

    # Count the number of ids whose settings differ from the default
    diff_count = 0
    for identifier, setting in file_data.items():
        if identifier =="343202616395694083":
            print(f"{list_key} NARUTO SERVER: {setting}")
        if setting != default_value:
            diff_count += 1

    differences_summary[list_key] = diff_count
    # print(f"{list_key}: {diff_count} ids have settings different from default.")

# Optionally, print a summary of the differences
print("\nSummary of differences:")
print(differences_summary)