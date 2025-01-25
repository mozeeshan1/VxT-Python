import aiomysql
import json

# Path to your JSON file
json_file_path = "path_to_your_list.json"

async def migrate_to_db():
    async with aiomysql.connect(
        host="db-buf-05.sparkedhost.us", user="u73567_6cNajMwxfR",
        password="iK=HJqi6VtH9UhpsaUDQ.^uH", db="s73567_test-database"
    ) as conn:
        async with conn.cursor() as cursor:
            # Load JSON file
            with open(json_file_path, "r") as f:
                data = json.load(f)
            
            for guild_id, settings in data.items():
                # Insert into guild_settings table
                await cursor.execute(
                    "INSERT INTO guild_settings (guild_id, settings) VALUES (%s, %s) "
                    "ON DUPLICATE KEY UPDATE settings = VALUES(settings)",
                    (guild_id, json.dumps(settings))
                )
            await conn.commit()

# Run the script
asyncio.run(migrate_to_db())
