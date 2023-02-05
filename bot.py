import discord
import json

with open("config.json", "r") as f:
    config = json.load(f)

def run_bot():
    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f"{client.user} is now running")

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        p_message = message.content.lower()

        if p_message == "hello":
            await message.channel.send("bonjour")


    client.run(config['token'])