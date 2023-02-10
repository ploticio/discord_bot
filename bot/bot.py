import discord
from discord.ext import commands
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
    async def load(ctx, cog: str):
        await bot.load_extension(f"cogs.{cog}")

    @bot.command()
    async def unload(ctx, cog: str):
        await bot.unload_extension(f"cogs.{cog}")

    @bot.command()
    async def reload(ctx, cog: str):
        await bot.reload_extension(f"cogs.{cog}")

    bot.run(config.TOKEN)