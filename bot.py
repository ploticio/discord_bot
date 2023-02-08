import config
import discord
from discord.ext import commands
import json
import re
import os

def run_bot():
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

    @bot.event
    async def on_ready():
        print(f"{bot.user} is now running")

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        for key in config.NAUGHTY_WORDS:
            for word in config.NAUGHTY_WORDS[key]:
                if re.search(r'\b%s\b' % word, message.content.lower()):
                    await message.add_reaction("🤨")
                    await message.add_reaction("📸")
                    await message.reply(f"WOAH 😱😱😱 {message.guild.owner.mention} {message.guild.owner.mention} {message.guild.owner.mention}")

        await bot.process_commands(message)

    @bot.command()
    async def hello(ctx, user: discord.User):
        await ctx.send(f"Hello there {user.mention}")
    
    @bot.command()
    async def count(ctx, user: discord.User):
        final_count = {word: 0 for word in config.NAUGHTY_WORDS}

        # Text history read in as JSON
        await ctx.send("Reading history...")
        for filename in os.listdir("data/"):
            with open(os.path.join("data/", filename), "r") as f:
                data = json.load(f)

            for subdict in data['messages']:
                if subdict['author']['id'] == str(user.id): 
                    for key in config.NAUGHTY_WORDS:
                        for word in config.NAUGHTY_WORDS[key]:
                            found = len(re.findall(r'\b%s\b' % word, subdict['content'].lower()))
                            if found > 0:
                                final_count[key] += found
                                print(subdict['content'].lower())
        
        # Most recent messages
        for channel in ctx.guild.text_channels:
                try:
                    messages = [message async for message in channel.history(limit=200) 
                                if message.author == user]
                    for m in messages:
                        for key in config.NAUGHTY_WORDS:
                            for word in config.NAUGHTY_WORDS[key]:
                                if re.search(r'\b%s\b' % word, m.content.lower()):
                                    final_count[key] += 1
                except:
                    continue

        for key in final_count:
            msg = await ctx.send(f"Number of {key} detected: {final_count[key]}")
            if final_count[key] == 1:
                await msg.add_reaction("🤨")
            elif final_count[key] > 1 and final_count[key] < 10:
                await msg.add_reaction("🤨")
                await msg.add_reaction("📸")
            elif final_count[key] >= 10 and final_count[key] < 15:
                await msg.add_reaction("💀")
            else:
                await msg.add_reaction("😱")
                await msg.add_reaction("🇧")
                await msg.add_reaction("🇷")
                await msg.add_reaction("🇴")

        

    bot.run(config.TOKEN)