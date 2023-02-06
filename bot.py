import discord
import config

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

        ### WORD COUNTER ###
        if p_message == "$count":
            await message.channel.send("Counting frogs...")
            for channel in message.guild.text_channels:
                messages = [m async for m in channel.history() if message.author == m.author]
                for m in messages:
                    if "frog" in m.content:
                        counter += 1

    client.run(config.TOKEN)