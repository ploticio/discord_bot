import config
import discord
from discord.ext import commands

def run_bot():
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

    @bot.event
    async def on_ready():
        print(f"{bot.user} is now running")

    @bot.command()
    async def hello(ctx, user: discord.User):
        await ctx.send(f"Hello there {user.mention}")
    
    @bot.command()
    async def count(ctx, user: discord.User):
        counter = 0
        await ctx.send("Counting words...")
        for channel in ctx.guild.text_channels:
                messages = [message async for message in channel.history() if m.author == user]
                for m in messages:
                    if "frog" in m.content.lower():
                        counter += 1
        
        await ctx.send(f"Number of frogs detected: {counter}")

    bot.run(config.TOKEN)