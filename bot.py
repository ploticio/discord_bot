import discord
from discord.ext import commands
from cogs.counters import Counters
import config

def run_bot():
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

    @bot.event
    async def on_ready():
        print(f"{bot.user} is now running")

        for cogfile in config.COGS_DIR.glob("*.py"):
            if cogfile.name != "__init__.py":
                await bot.load_extension(f"cogs.{cogfile.name[:-3]}")
        

    @bot.command()
    async def hello(ctx, user: discord.User):
        await ctx.send(f"Hello there {user.mention}")

    bot.run(config.TOKEN)